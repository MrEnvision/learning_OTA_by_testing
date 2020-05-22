import queue
import time
import copy
from normalLearning.ota import buildAssistantOTA
from normalLearning.otatable import init_table_normal, make_closed, make_consistent, add_ctx_normal
from normalLearning.hypothesis import to_fa, fa_to_ota
from normalLearning.pac_equiv import pac_equivalence_query, minimizeCounterexample


def learnOTA(targetSys, inputs, upperGuard, epsilon, delta, stateNum, debug_flag):
    targetFullSys = buildAssistantOTA(targetSys, 's')
    upperGuard = targetSys.max_time_value()

    need_to_explore = queue.PriorityQueue()
    for table in init_table_normal(inputs, targetFullSys):
        need_to_explore.put((table.effective_len(), table))

    # List of existing counterexamples
    prev_ctx = []

    # Current number of tables
    t_number = 0
    eq_total_time = 0
    eq_number = 0
    target = None

    while True:
        if need_to_explore.qsize() == 0:
            break
        depth, current_table = need_to_explore.get()
        t_number = t_number + 1

        if t_number % 1 == 0:
            print(t_number, need_to_explore.qsize(), current_table.effective_len())
        if debug_flag:
            print("Table " + str(t_number) + " is as follow, %s has parent %s by %s" % (current_table.id, current_table.parent, current_table.reason))
            current_table.show()
            print("--------------------------------------------------")

        # First check if the table is closed
        flag_closed, new_S, new_R, move = current_table.is_closed()
        if not flag_closed:
            if debug_flag:
                print("------------------make closed--------------------------")
            temp_tables = make_closed(new_S, new_R, move, current_table, inputs, targetFullSys)
            if len(temp_tables) > 0:
                for table in temp_tables:
                    need_to_explore.put((table.effective_len(), table))
            continue

        # If is closed, check if the table is consistent
        flag_consistent, new_a, new_e_index, reset_index_i, reset_index_j, reset_i, reset_j = current_table.is_consistent()
        if not flag_consistent:
            if debug_flag:
                print("------------------make consistent--------------------------")
            temp_tables = make_consistent(new_a, new_e_index, reset_index_i, reset_index_j, reset_i, reset_j, current_table, inputs, targetFullSys)
            if len(temp_tables) > 0:
                for table in temp_tables:
                    need_to_explore.put((table.effective_len(), table))
            continue

        # If prepared, check conversion to FA
        fa_flag, fa, sink_name = to_fa(current_table, t_number)
        if not fa_flag:
            continue

        # Can convert to FA: convert to OTA and test equivalence
        h = fa_to_ota(fa, sink_name, inputs, t_number)
        eq_start = time.time()
        equivalent, ctx = True, None
        if prev_ctx is not None:
            for ctx in prev_ctx:
                teacher_res = targetFullSys.is_accepted_delay(ctx.tws)
                hypothesis_res = h.is_accepted_delay(ctx.tws)
                if teacher_res != hypothesis_res and hypothesis_res != -2:
                    equivalent, ctx = False, ctx
                    ctx = minimizeCounterexample(targetFullSys, h, ctx)

        if equivalent:
            targetFullSys.equiv_query_num += 1
            equivalent, ctx, _ = pac_equivalence_query(targetSys, upperGuard, targetFullSys, h, targetFullSys.equiv_query_num, epsilon, delta)

        if not equivalent:
            print(ctx.tws)

        # Add counterexample to prev list
        if not equivalent and ctx not in prev_ctx:
            prev_ctx.append(ctx)
        eq_end = time.time()
        eq_total_time = eq_total_time + eq_end - eq_start
        eq_number = eq_number + 1
        if not equivalent:
            temp_tables = add_ctx_normal(ctx.tws, current_table, targetFullSys)
            if len(temp_tables) > 0:
                for table in temp_tables:
                    need_to_explore.put((table.effective_len(), table))
        else:
            target = copy.deepcopy(h)
            break

    if target is None:
        return False, target, 0, 0, 0, 0, 0
    else:
        mqNumCache = targetFullSys.mem_query_num
        mqNum = len(targetFullSys.membership_query)
        eqNumCache = len(prev_ctx) + 1
        eqNum = targetFullSys.equiv_query_num
        tableNum = t_number
        return True, target, mqNumCache, mqNum, eqNumCache, eqNum, tableNum
