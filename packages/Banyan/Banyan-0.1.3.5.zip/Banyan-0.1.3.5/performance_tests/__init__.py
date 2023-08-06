from __future__ import print_function
from pylab import *
from matplotlib.pyplot import *

import _dict_it
import _dict_find
import _dict_update_slice
import _set_it
import _set_insert
import _set_find
import _set_find_local
import _set_create
import _set_insert_sort
import _set_insert_erase
import _set_insert_rank
import _set_insert_min_gap
import _set_erase_slice
import _set_insert_overlapping_intervals

    
_run_insert_overlapping_intervals = False
_run_it = False
_run_insert_sort = False
_run_insert_rank = True
_run_insert_erase = False
_run_find = False
_run_erase_slice = False
_run_update_slice = False
_run_find_local = False
_run_create = False
_run_insert_min_gap = False


class _Recorder(object):
    def __init__(self):
        self._x_vals = []
        self._results = dict([])

    def add_results(self, x_val, res):
        print(res)
        self._x_vals.append(x_val)
        for n in list(res.keys()):
            self._results.setdefault(n, []).append(res[n])

    def maxes_res(self):
        maxes = [(n, max(res)) for n, res in self._results.items()]
        maxes.sort(key = lambda nm: nm[1])
        
        return maxes, self._results

        
def _single_malt(fn, x_range, num_its, algs, title, f_name):
    fig = figure()
    ax = subplot(111)

    xlabel('# Items')
    ylabel('Time (sec.)')
    ticklabel_format(style = 'sci', axis='y', scilimits=(0,0))        
    
    r = _Recorder()
    for x in x_range:
        print('running', f_name, x)
        r.add_results(x, fn(algs, x, num_its))
    maxes, res = r.maxes_res()

    for n in [nm[0] for nm in maxes]:
        ax.plot(x_range, res[n], label = n)
        
    box = ax.get_position()    
    ax.set_position([box.x0, box.y0 + box.height * 0.3, box.width, box.height * 0.72])
    ax.legend(
        [n for (n, m) in maxes], 
        loc = 'upper center', 
        bbox_to_anchor = (0.5, -0.1),
        ncol = 2 if len(maxes) > 5 else 1)

    text(0.5, 1.08, title,
         horizontalalignment='center',
         fontsize = 13,
         transform = ax.transAxes)        
    # subtitle(title)        

    savefig(f_name)    
    

_banyans = [
    'banyan_red_black_tree', 
    'banyan_splay_tree', 
    'banyan_sorted_list',
    'banyan_red_black_tree_gen', 
    'banyan_splay_tree_gen', 
    'banyan_sorted_list_gen']    


if __name__ == '__main__':
    #num_its = 1
    num_its = 30

    base = 50
    #base = 1 
    
    if _run_insert_overlapping_intervals:
        _single_malt(
            _set_insert_overlapping_intervals.run_tests, 
            [base * i for i in range(1, 10)], 
            50 * num_its, 
            ['banyan_red_black_tree', 'bx'],
            'All Items Insert + Last Interval Overlaps As A Function Of # Items',
            'IntSetInsertOverlappingCompetitive.png')

        _single_malt(
            _set_insert_overlapping_intervals.run_tests, 
            [base * i for i in range(1, 10)], 
            50 * num_its, 
            ['banyan_red_black_tree', 'banyan_red_black_tree_float', 'banyan_red_black_tree_gen', 'bx'],
            'All Items Insert + Last Interval Overlaps As A Function Of # Items',
            'IntSetInsertOverlappingAll.png')

    if _run_find_local:
        _single_malt(
            _set_find_local.run_tests, 
            [base * i for i in range(1, 10)], 
            500 * num_its, 
            _banyans + ['blist', 'btrees', 'set'],
            'All Items Repeated Find Time As A Function Of # Items',
            'IntSetFindLocalAll.png')

        _single_malt(
            _set_find_local.run_tests, 
            [base * i for i in range(1, 10)], 
            500 * num_its, 
            _banyans + ['btrees', 'set'],
            'All Items Repeated Find Time As A Function Of # Items',
            'IntSetFindLocalAllNoBList.png')
            
        _single_malt(
            _set_find_local.run_tests, 
            [base * i for i in range(1, 10)], 
            500 * num_its, 
            ['banyan_red_black_tree', 'banyan_splay_tree', 'set', 'btrees'],
            'All Items Repeated Find Time As A Function Of # Items',
            'IntSetFindLocalCompetitive.png')

    if _run_update_slice:
        _single_malt(
            _dict_update_slice.run_tests, 
            [base * i for i in range(1, 10)], 
            50 * num_its, 
            _banyans + ['bintrees', 'btrees', 'blist', 'dict'],
            'Update Fixed-Size Slice As A Function Of # Items',
            'IntDictUpdateSliceAll.png')    

        _single_malt(
            _dict_update_slice.run_tests, 
            [base * i for i in range(1, 10)], 
            50 * num_its, 
            _banyans + ['btrees', 'dict'],
            'Update Fixed-Size Slice As A Function Of # Items',
            'IntDictUpdateSliceAllNoBListBintrees.png')    

        _single_malt(
            _dict_update_slice.run_tests, 
            [base * i for i in range(1, 10)], 
            50 * num_its, 
            ['banyan_red_black_tree', 'btrees', 'dict'],
            'Update Fixed-Size Slice As A Function Of # Items',
            'IntDictUpdateSliceCompetitive.png')    

    if _run_erase_slice:
        _single_malt(
            _set_erase_slice.run_tests, 
            [base * i for i in range(1, 10)], 
            50 * num_its, 
            _banyans + ['bintrees', 'set'],
            'Erase Fixed-Size Slice As A Function Of # Items',
            'IntSetEraseSliceAll.png')    
    
        _single_malt(
            _set_erase_slice.run_tests, 
            [base * i for i in range(1, 10)], 
            50 * num_its, 
            ['banyan_red_black_tree', 'bintrees', 'set'],
            'Erase Fixed-Size Slice As A Function Of # Items',
            'IntSetEraseSliceCompetitive.png')    

    if _run_find:
        _single_malt(
            _set_find.run_tests, 
            [base * i for i in range(1, 10)], 
            200 * num_its, 
            [
                'banyan_red_black_tree', 
                'banyan_red_black_tree_rank_updator', 
                'btrees', 
                'set'],
            'All Items Find Time As A Function Of # Items',
            'IntSetFindCompetitiveWithRankUpdator.png')    

        _single_malt(
            _dict_find.run_tests, 
            [base * i for i in range(1, 10)], 
            20 * num_its, 
            _banyans + ['blist', 'btrees', 'dict'],
            'All Items Find Time As A Function Of # Items',
            'IntDictFindAll.png')    
    
        _single_malt(
            _dict_find.run_tests, 
            [base * i for i in range(1, 10)], 
            200 * num_its, 
            _banyans + ['btrees', 'dict'],
            'All Items Find Time As A Function Of # Items',
            'IntDictFindAllNoBList.png')    

        _single_malt(
            _dict_find.run_tests, 
            [base * i for i in range(1, 10)], 
            200 * num_its, 
            ['banyan_red_black_tree', 'btrees', 'dict'],
            'All Items Find Time As A Function Of # Items',
            'IntDictFindCompetitive.png')    

        _single_malt(
            _set_find.run_tests, 
            [base * i for i in range(1, 10)], 
            20 * num_its, 
            _banyans + ['blist', 'btrees', 'set'],
            'All Items Find Time As A Function Of # Items',
            'IntSetFindAll.png')

        _single_malt(
            _set_find.run_tests, 
            [base * i for i in range(1, 10)], 
            200 * num_its, 
            _banyans + ['btrees', 'set'],
            'All Items Find Time As A Function Of # Items',
            'IntSetFindAllNoBList.png')
            
        _single_malt(
            _set_find.run_tests, 
            [base * i for i in range(1, 10)], 
            200 * num_its, 
            ['banyan_red_black_tree', 'set', 'btrees'],
            'All Items Find Time As A Function Of # Items',
            'IntSetFindCompetitive.png')

        _single_malt(
            _set_find.run_tests, 
            [base * i for i in range(1, 10)], 
            300 * num_its, 
            ['banyan_red_black_tree', 'banyan_sorted_list', 'set', 'btrees'],
            'All Items Find Time As A Function Of # Items',
            'IntSetFindCompetitiveWithSortedList.png')

        _single_malt(
            _set_find.run_tests, 
            [base * i for i in range(1, 10)], 
            20 * num_its, 
            ['banyan_red_black_tree', 'banyan_splay_tree', 'set', 'btrees'],
            'All Items Find Time As A Function Of # Items',
            'IntSetFindCompetitiveWithSplayTree.png')    

    if _run_it:
        _single_malt(
            _dict_it.run_tests, 
            [base * i for i in range(1, 10)], 
            5000 * num_its, 
            ['banyan_red_black_tree', 'banyan_sorted_list', 'set', 'btrees'],
            'Sorted Iteration Time As A Function Of # Items',
            'IntSetItCompetitiveWithSortedList.png')

        _single_malt(
            _set_it.run_tests, 
            [base * i for i in range(1, 10)], 
            1000 * num_its, 
            _banyans + ['bintrees', 'blist', 'btrees', 'set'],
            'Sorted Iteration Time As A Function Of # Items',
            'IntSetItAll.png')

        _single_malt(
            _set_it.run_tests, 
            [base * i for i in range(1, 10)], 
            1000 * num_its, 
            _banyans + ['btrees', 'set'],
            'Sorted Iteration Time As A Function Of # Items',
            'IntSetItAllNoBListBintrees.png')

    if _run_insert_sort:    
        _single_malt(
            _set_insert_sort.run_tests, 
            [base * i for i in range(1, 10)], 
            15 * num_its, 
            _banyans + ['bintrees', 'blist', 'btrees', 'set'],
            'Insert + Sorted Iteration Time As A Function Of # Items',
            'IntSetInsertSortAll.png')

    if _run_insert_sort:    
        _single_malt(
            _set_insert_sort.run_tests, 
            [base * i for i in range(1, 10)], 
            15 * num_its, 
            _banyans + ['btrees', 'set'],
            'Insert + Sorted Iteration Time As A Function Of # Items',
            'IntSetInsertSortAllNoBlistBintrees.png')

        _single_malt(
            _set_insert_sort.run_tests, 
            [30 * base * i for i in range(1, 10)], 
            3, 
            ['banyan_red_black_tree', 'set', 'btrees'],
            'Insert + Sorted Iteration Time As A Function Of # Items',
            'IntSetInsertSortCompetitiveLarger.png')

        _single_malt(
            _set_insert_sort.run_tests, 
            [base * i for i in range(1, 10)], 
            35 * num_its, 
            ['banyan_red_black_tree', 'set', 'btrees'],
            'Insert + Sorted Iteration Time As A Function Of # Items',
            'IntSetInsertSortCompetitive.png')

    if _run_insert_rank:            
        _single_malt(
            _set_insert_rank.run_tests, 
            [base * i for i in range(1, 10)], 
            30, 
            _banyans + ['banyan_red_black_tree_rank_updator', 'btrees', 'set'], 
            'Insert + Rank Time As A Function Of # Items',
            'IntSetInsertRankAllNoBListBintreesWithRankUpdator.png')

        _single_malt(
            _set_insert_rank.run_tests, 
            [base * i for i in range(1, 10)], 
            30, 
            _banyans + ['banyan_red_black_tree_rank_updator', 'bintrees', 'blist', 'btrees', 'set'], 
            'Insert + Rank Time As A Function Of # Items',
            'IntSetInsertRankAllWithRankUpdator.png')

        _single_malt(
            _set_insert_rank.run_tests, 
            [base * i for i in range(1, 10)], 
            30, 
            ['banyan_red_black_tree', 'banyan_red_black_tree_rank_updator', 'set', 'btrees'], 
            'Insert + Rank Time As A Function Of # Items',
            'IntSetInsertRankCompetitiveWithRankUpdator.png')

    if _run_insert_min_gap:            
        _single_malt(
            _set_insert_min_gap.run_tests, 
            [base * i for i in range(1, 10)], 
            20, 
            _banyans + ['banyan_red_black_tree_min_gap_updator', 'btrees', 'set'], 
            'Insert + Min-Gap Time As A Function Of # Items',
            'IntSetInsertMinGapAllNoBListBintreesWithMinGapUpdator.png')

        _single_malt(
            _set_insert_min_gap.run_tests, 
            [base * i for i in range(1, 10)], 
            20, 
            _banyans + ['banyan_red_black_tree_min_gap_updator', 'bintrees', 'blist', 'btrees', 'set'], 
            'Insert + Min-Gap Time As A Function Of # Items',
            'IntSetInsertMinGapAllWithMinGapUpdator.png')

        _single_malt(
            _set_insert_min_gap.run_tests, 
            [base * i for i in range(1, 10)], 
            20, 
            ['banyan_red_black_tree', 'banyan_red_black_tree_min_gap_updator', 'set', 'btrees'], 
            'Insert + Min-Gap Time As A Function Of # Items',
            'IntSetInsertMinGapCompetitiveWithMinGapUpdator.png')

    if _run_insert_erase:            
        _single_malt(
            _set_insert_erase.run_tests, 
            [base * i for i in range(1, 10)], 
            30 * num_its, 
            ['banyan_red_black_tree', 'banyan_red_black_tree_rank_updator', 'set', 'btrees'], 
            'Insert + Erase Time As A Function Of # Items',
            'IntSetInsertEraseCompetitiveWithRankUpdator.png')

        _single_malt(
            _set_insert_erase.run_tests, 
            [10 * base * i for i in range(1, 10)], 
            3 * num_its, 
            ['banyan_red_black_tree', 'banyan_red_black_tree_rank_updator', 'set', 'btrees'], 
            'Insert + Erase Time As A Function Of # Items',
            'IntSetInsertEraseCompetitiveWithNodeUpdatorLonger.png')

        _single_malt(
            _set_insert_erase.run_tests, 
            [base * i for i in range(1, 10)], 
            100 * num_its, 
            ['banyan_red_black_tree', 'set', 'btrees'], 
            'Insert + Erase Time As A Function Of # Items',
            'IntSetInsertEraseCompetitive.png')

        _single_malt(
            _set_insert_erase.run_tests, 
            [base * i for i in range(1, 10)], 
            100 * num_its, 
            ['banyan_red_black_tree', 'banyan_sorted_list', 'set', 'btrees'], 
            'Insert + Erase Time As A Function Of # Items',
            'IntSetInsertEraseCompetitiveWithSortedList.png')

        _single_malt(
            _set_insert_erase.run_tests, 
            [base * i for i in range(1, 10)], 
            100 * num_its, 
            _banyans + ['bintrees', 'blist', 'btrees', 'set'], 
            'Insert + Erase Time As A Function Of # Items',
            'IntSetInsertEraseAll.png')

        _single_malt(
            _set_insert_erase.run_tests, 
            [base * i for i in range(1, 10)], 
            100 * num_its, 
            _banyans + ['bintrees', 'btrees', 'set'], 
            'Insert + Erase Time As A Function Of # Items',
            'IntSetInsertEraseAllNoBList.png')

        _single_malt(
            _set_insert_erase.run_tests, 
            [30 * base * i for i in range(1, 10)], 
            3, 
            ['banyan_red_black_tree', 'banyan_sorted_list', 'set', 'btrees'], 
            'Insert + Erase Time As A Function Of # Items',
            'IntSetInsertEraseCompetitiveLonger.png')

    if _run_create:            
        _single_malt(
            _set_create.run_tests, 
            [base * i for i in range(1, 10)], 
            30 * num_its, 
            ['banyan_red_black_tree', 'banyan_sorted_list', 'set', 'btrees'], 
            'Create Time As A Function Of # Items',
            'IntSetCreateCompetitiveWithSortedList.png')
            
        _single_malt(
            _set_create.run_tests, 
            [base * i for i in range(1, 10)], 
            30 * num_its, 
            _banyans + ['bintrees', 'blist', 'btrees', 'set'],
            'Create Time As A Function Of # Items',
            'IntSetCreateAll.png')

        _single_malt(
            _set_create.run_tests, 
            [base * i for i in range(1, 10)], 
            30 * num_its, 
            _banyans + ['btrees', 'set'],
            'Create Time As A Function Of # Items',
            'IntSetCreateAllNoBListBintrees.png')


