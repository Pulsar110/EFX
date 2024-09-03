import random
import copy 
import time

# Number of agents 
N = 3
N_arr = list(range(N))
# Number of experiment to run for each sampled cost 
N_EXP = 50000
COST_FUNCTION = sum
# COST_RND = random.random
COST_RND = lambda: random.randrange(1,1000)


# Number of items
for i in range(8,9):
    M = i
    M_arr = list(range(M))


    ### Iterate through all assignments (N^M possibilities)
    # yield a list of M elements, each indicating the assigmennt of 
    # item (index) to wich agent (value)

    def _iter_assignments(m_arr, n_arr, ass_arr):
        for i in n_arr:
            ass_arr[m_arr[0]] = i
            if len(m_arr) == 1:
                yield ass_arr
            else:
                yield from _iter_assignments([m_arr[j] for j in range(1,len(m_arr))], 
                                             n_arr, ass_arr)

    def iter_assignments():
        yield from  _iter_assignments(M_arr, N_arr, copy.copy(M_arr))

    ### END

    def format_cost_arr():
        # Set random cost for each agent and item (NxM)
        cost_arr = [[COST_RND() for _ in M_arr] for _ in N_arr]
        return cost_arr

    def format_item_arr(ass_arr):
        # Get item array for each agent
        item_arr = [None]*N
        for n in N_arr:
            item_arr[n] = [i for i in M_arr if ass_arr[i] == n]
        return item_arr

    def get_cost(agent_n, item_arr_n, cost_arr):
        return COST_FUNCTION([cost_arr[agent_n][i] for i in item_arr_n])

    def iter_remove_one_item_cost(agent_n, item_arr_n, cost_arr):
        for rem_i in item_arr_n:
            removed_item_arr = [i for i in item_arr_n if i != rem_i]
            yield get_cost(agent_n, removed_item_arr, cost_arr)

    def efx_ef_satisfied(item_arr, cost_arr):
        n_ef = 0
        for n in N_arr:
            # if only has one item or less, then the EFX is satisfied 
            if len(item_arr[n]) <= 1:
                continue
            # compute cost of other people
            cost_rest = [get_cost(n, item_arr[i], cost_arr) for i in N_arr if i != n]
            # remove an item assignmed to that agent n
            for cost_n in iter_remove_one_item_cost(n, item_arr[n], cost_arr):
                if cost_n > min(*cost_rest):
                    # print('Item assignment:', item_arr)
                    # print('Cost value:', cost_arr)
                    # print('Removing item', rem_i, 'from agent', n, 'results cost', cost_n)
                    # print('Others\' costs:', cost_rest)
                    return False, n_ef
            if get_cost(n, item_arr[n], cost_arr) <= min(*cost_rest):
                n_ef += 1
        return True, n_ef

    print_one_found_example_per_n_ef = [True]*(N+1)

    print('M=%d, N=%d\n'%(M,N))

    statistics_efx = []
    statistics_ef = []
    statistics_n_ef = []
    start_time = time.time()
    for n in range(N_EXP):
        random.seed(n)
        cost_arr = format_cost_arr()
        n_runs = 0
        found_efx = 0
        found_ef = 0
        for ass_arr in iter_assignments():
            # print('Assignment', ass_arr)
            item_arr = format_item_arr(ass_arr)
            is_efx, n_ef = efx_ef_satisfied(item_arr, cost_arr)
            is_ef = n_ef==N
            if is_efx:
                found_efx += 1
                statistics_n_ef.append(n_ef)
                if print_one_found_example_per_n_ef[n_ef]:
                    print('EFX example found with %d EF agents' % (n_ef))
                    print('(additive) Valuation (%d/%d)'%(n+1, N_EXP))
                    for i in N_arr:
                        print('Agent n=', i, cost_arr[i])
                    
                    print('\nFound allocation %d/%d\n'%(n_runs,int(N**M)))
                    for i in N_arr:
                        print('Agent n=', i)
                        print('\tBundle:', item_arr[i])
                        c = [cost_arr[i][j] for j in item_arr[i]]
                        print('\tCost:', c)
                        print('\tBundle cost:', sum(c))
                        print('\tCost for bundle - item x:', end=' ')
                        for cost_n in iter_remove_one_item_cost(i, item_arr[i], cost_arr):
                            print(cost_n, end=' ')
                        print('\n\tCost for other bundle:', *[get_cost(i, item_arr[j], cost_arr) for j in N_arr if i != j])
                        print('')
                    print_one_found_example_per_n_ef[n_ef] = False
            if is_ef:
                found_ef += 1
            n_runs += 1
        statistics_efx.append(found_efx)
        statistics_ef.append(found_ef)
        if found_ef == 0:
            print('Found sample with no EF')
            print('(additive) Valuation (%d/%d)'%(n+1, N_EXP))
            for i in N_arr:
                print('Agent n=', i, cost_arr[i])
            print('')


    print('\nStatistics\n')

    def print_statistics(stats, name):
        avg = sum(stats)/N_EXP
        max_ = max(stats)
        min_ = min(stats)
        print('Average number of %s allocations over %d samples: %.2f/%d = %.2f %%' % (name, N_EXP, avg, n_runs, avg/n_runs*100))
        print('Max: %d/%d = %.2f %%' % (max_, n_runs, max_/n_runs*100))
        print('Min: %d/%d = %.2f %%' % (min_, n_runs, min_/n_runs*100))
        std = sum([(s-avg)**2/(N_EXP-1) for s in stats])**(1/2)
        std_perc = sum([(s/n_runs*100-avg/n_runs*100)**2/(N_EXP-1) for s in stats])**(1/2)
        print('STD: %.2f (%.2f for percentage)'%(std, std_perc))

    print_statistics(statistics_efx, 'EFX')
    print_statistics(statistics_ef, 'EF')

    avg = sum(statistics_n_ef)/len(statistics_n_ef)
    max_ = max(statistics_n_ef)
    min_ = min(statistics_n_ef)
    print('Average number of EF agents when EFX: %.2f' % (avg))
    print('Max: %d' % (max_))
    print('Min: %d' % (min_))

    print('Run time: %.2f sec' % (time.time()-start_time))

    print('\n------------\n')
