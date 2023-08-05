// Date converter for dates in the format DD.MM.YYYY (the format must match in any case !!!!!)

function dateConverter(s)
{
    var l = s.length;
    var sum=0;
    var hours=0;
    var minutes=0;
    var seconds=0;

    var day = parseFloat(s.substring(0, 2));
    var month = parseFloat(s.substring(3, 5));
    var year = parseFloat(s.substring(6, 10));

    if (l >= 11) 
        hours = parseFloat(s.substring(11, 13));
    if (l >= 14) 
        minutes = parseFloat(s.substring(14, 16));
    if (l >= 16) 
        seconds = parseFloat(s.substring(17, 19));

    sum = year*365 +  month*30 + day + hours/24.0 + minutes/1440.0 + seconds/86400;
    return sum;
}
SortableTable.prototype.addSortType("DATE", dateConverter);
SortableTable.prototype.addSortType("Date", dateConverter);

