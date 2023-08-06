
  PyvtTbl
=======================================================================
  Python pivot table (contingency tables) with sqlite3 
  backend.

=======================================================================

  Author: Roger Lew
  Author  email: rogerlew@gmail.com
  Home:   http://code.google.com/p/pyvttbl/
=======================================================================

  Change Log

  v 0.5.2.2
    - fix in anova1way tukey post-hoc comparisons. observed values were
      not calculated correctly when the number of comparisons did not
      match the number of observations. Most of the time would lead to
      conservative comparisons (N > # of comparisons)

  v 0.5.2.1
    - dumbed down the tick label formatting on scatter_matrix

  v 0.5.2.0
    - PyvtTbl.__iter__ defaults to super now that __getitem__ is working
      - when not indexing a single element PyvtTbl will always be at
        least 2-dimensional
    - made plotting API more consistent
    - extended test coverage
    - Everything now has at least some documentation

  v 0.5.1.0
    - Implemented PyvtTbl.__getitem__
    - PyvtTbl should always have >= 2 dimensions
    - Testing coverage for PyvtTbl slicing
    - More Sphinx documentation
    - Removed PyvtTbl.write

  v 0.5.0.0
    - NOT BACKWARDS COMPATIBLE WITH PREVIOUS PYPI RELEASES
    - Sphinx documentation
    
  v 0.4.4.1
    - Test coverage
    - DataFrame.row_iter iterator

  v 0.4.4.0
    - PyvtTbl inherents numpy.ma.MaskedArray
    - Implemented PyvtTbl.ndenumerate iterator

  v 0.4.3.0
    - DataFrame holds numpy.arrays and numpy.ma.arrays (masked arrays)
    - keys just have to be hashable (strings, tups, lists). Strings
      can contain special characters
    - No DataFrames.names() method
    - added DataFrames.get_sqltype()
    - added DataFrames.get_nptype()
    - nose testing
    - reorganized

  v 0.4.2.0
    - implemented scatter matrix plotting

  v 0.4.1.0
    - added Pyvttbl.to_dataframe method
    - fixed Anova so it can transform data in lists
    - fixed DataFrame.anova wrapper so 'SNK' can be specified as
      posthoc test

  v 0.4.0.2
    - fixed dependency issue with dictset and pystaggrelite3.
    - They should install automatically through easy_install.

  v 0.4.0.1
    - fixed issue 4 were column names or row labels could
      exceed pivot table with non-factorial data

  v 0.4.0.0
    - Finalized Tukey and SNK posthoc comparisons in Anova1way
    - Added posthoc power analyses in Anova, Anova1way, Ttest,
      ChiSquare1way, and ChiSquare2way

  v 0.3.6.7
    - fixed bug in anova.py that prevented output when subject 
      variable was not 'SUBJECT'
    - fixed tick label issue with interaction_plot

  v 0.3.6.6
    - fixed bug with interaction_plots with subplots

  ... see repo

=======================================================================
