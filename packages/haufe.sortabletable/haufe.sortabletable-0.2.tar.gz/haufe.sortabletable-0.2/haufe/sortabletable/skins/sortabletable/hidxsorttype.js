// HIDX|LIDX|PID to int

function indexConverter(s)
{
    var idx = 0;

    if (s.indexOf('HIT')==0) 
	    idx = s.substring(3, s.length);                   
    else if (s.indexOf('HI')==0 || s.indexOf('PI')==0 || s.indexOf('LI')==0) 
	    idx = s.substring(2, s.length);                   
    else
        idx = s

	return parseInt(idx);
}

SortableTable.prototype.addSortType("HIDX", indexConverter);
SortableTable.prototype.addSortType("LIDX", indexConverter);
SortableTable.prototype.addSortType("PID", indexConverter);
SortableTable.prototype.addSortType("Index", indexConverter);
