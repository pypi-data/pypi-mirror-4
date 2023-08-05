// Date converter for dates in the format DD.MM.YY (the format must match in any case !!!!!)
// $Id: germandatesorttype.js,v 1.2 2007-04-16 14:12:43 hrs2test Exp $

function germanDateConverter(s)
{
    var l = s.length;
    var sum=0;
    var hours=0;
    var minutes=0;
    var seconds=0;

    var day = parseFloat(s.substring(0, 2));
    var month = parseFloat(s.substring(3, 5));
    var year = parseFloat(s.substring(6, 8));

    if (l >= 9) 
        hours = parseFloat(s.substring(9, 11));
    if (l >= 12) 
        minutes = parseFloat(s.substring(12, 14));
    if (l >= 14) 
        seconds = parseFloat(s.substring(15, 17));

    sum = year*365 +  month*30 + day + hours/24.0 + minutes/1440.0 + seconds/86400;
    return sum;
}

SortableTable.prototype.addSortType("GermanDate", germanDateConverter);
