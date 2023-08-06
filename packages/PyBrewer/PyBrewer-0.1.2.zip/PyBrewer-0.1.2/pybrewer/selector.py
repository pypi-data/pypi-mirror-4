from brew import *
from collections import defaultdict

BuGn=['#F7FCFD', '#EDF8FB', '#E5F5F9', '#CCECE6', '#B2E2E2', '#99D8C9', '#66C2A4', '#41AE76','#2CA25F', '#238B45', '#006D2C', '#005824', '#00441B']
BuGn9=Brew('sequential', sequential_from_scheme(BuGn, 9), 'BuGn', colorblind_safe=True)
BuGn8=Brew('sequential', sequential_from_scheme(BuGn, 8), 'BuGn', colorblind_safe=True)
BuGn7=Brew('sequential', sequential_from_scheme(BuGn, 7), 'BuGn', colorblind_safe=True)
BuGn6=Brew('sequential', sequential_from_scheme(BuGn, 6), 'BuGn', colorblind_safe=True)
BuGn5=Brew('sequential', sequential_from_scheme(BuGn, 5), 'BuGn', colorblind_safe=True)
BuGn4=Brew('sequential', sequential_from_scheme(BuGn, 4), 'BuGn', colorblind_safe=True, print_safe=True)
BuGn3=Brew('sequential', sequential_from_scheme(BuGn, 3), 'BuGn', colorblind_safe=True, photocopy_safe=True, print_safe=True)

BuPu=['#F7FCFD', '#EDF8FB', '#E0ECF4', '#BFD3E6', '#B3CDE3', '#9EBCDA', '#8C96C6', '#8C6BB1', '#8856A7', '#88419D', '#810F7C', '#6E016B', '#4D004B']
BuPu9=Brew('sequential', sequential_from_scheme(BuPu, 9), 'BuPu', colorblind_safe=True)
BuPu8=Brew('sequential', sequential_from_scheme(BuPu, 8), 'BuPu', colorblind_safe=True)
BuPu7=Brew('sequential', sequential_from_scheme(BuPu, 7), 'BuPu', colorblind_safe=True)
BuPu6=Brew('sequential', sequential_from_scheme(BuPu, 6), 'BuPu', colorblind_safe=True)
BuPu5=Brew('sequential', sequential_from_scheme(BuPu, 5),'BuPu', colorblind_safe=True)
BuPu4=Brew('sequential', sequential_from_scheme(BuPu, 4),'BuPu', colorblind_safe=True, print_safe=True)
BuPu3=Brew('sequential', sequential_from_scheme(BuPu, 3),'BuPu', colorblind_safe=True, photocopy_safe=True, print_safe=True)

GnBu=['#F7FCF0', '#F0F9E8', '#E0F3DB', '#CCEBC5', '#BAE4BC', '#A8DDB5', '#7BCCC4', '#4EB3D3', '#43A2CA', '#2B8CBE', '#0868AC', '#08589E', '#084081']
GnBu9=Brew('sequential', sequential_from_scheme(GnBu, 9), 'GnBu', colorblind_safe=True)
GnBu8=Brew('sequential', sequential_from_scheme(GnBu, 8), 'GnBu', colorblind_safe=True)
GnBu7=Brew('sequential', sequential_from_scheme(GnBu, 7), 'GnBu', colorblind_safe=True)
GnBu6=Brew('sequential', sequential_from_scheme(GnBu, 6), 'GnBu', colorblind_safe=True)
GnBu5=Brew('sequential', sequential_from_scheme(GnBu, 5), 'GnBu', colorblind_safe=True, print_safe=True)
GnBu4=Brew('sequential', sequential_from_scheme(GnBu, 4), 'GnBu', colorblind_safe=True, print_safe=True)
GnBu3=Brew('sequential', sequential_from_scheme(GnBu, 3), 'GnBu', colorblind_safe=True, photocopy_safe=True, print_safe=True)

OrRd=['#FFF7EC', '#FEF0D9', '#FEE8C8', '#FDD49E', '#FDCCBA', '#FDBB84', '#FC8D59', '#EF6548', '#E34A33', '#D7301F', '#B30000', '#990000','#7F0000']
OrRd9=Brew('sequential', sequential_from_scheme(OrRd, 9), 'OrRd', colorblind_safe=True)
OrRd8=Brew('sequential', sequential_from_scheme(OrRd, 8), 'OrRd', colorblind_safe=True)
OrRd7=Brew('sequential', sequential_from_scheme(OrRd, 7), 'OrRd', colorblind_safe=True)
OrRd6=Brew('sequential', sequential_from_scheme(OrRd, 6), 'OrRd', colorblind_safe=True)
OrRd5=Brew('sequential', sequential_from_scheme(OrRd, 5), 'OrRd', colorblind_safe=True)
OrRd4=Brew('sequential', sequential_from_scheme(OrRd, 4), 'OrRd', colorblind_safe=True, photocopy_safe=True, print_safe=True)
OrRd3=Brew('sequential', sequential_from_scheme(OrRd, 3), 'OrRd', colorblind_safe=True, photocopy_safe=True, print_safe=True)

PuBu=['#FFF7FB', '$F6EFF7', '#F1EEF6', '#ECE7F2', '#D0D1E6', '#BDC9E1', '#A6BDDB', '#74A9CF', '#3690C0', '#2B8CBE', '#0570B0', '#045A8D', '#023858']
PuBu9=Brew('sequential', sequential_from_scheme(PuBu, 9), 'PuBu', colorblind_safe=True)
PuBu8=Brew('sequential', sequential_from_scheme(PuBu, 8), 'PuBu' ,colorblind_safe=True)
PuBu7=Brew('sequential', sequential_from_scheme(PuBu, 7), 'PuBu', colorblind_safe=True)
PuBu6=Brew('sequential', sequential_from_scheme(PuBu, 6), 'PuBu', colorblind_safe=True)
PuBu5=Brew('sequential', sequential_from_scheme(PuBu, 5), 'PuBu', colorblind_safe=True)
PuBu4=Brew('sequential', sequential_from_scheme(PuBu, 4), 'PuBu', colorblind_safe=True)
PuBu3=Brew('sequential', sequential_from_scheme(PuBu, 3), 'PuBu', colorblind_safe=True, print_safe=True, photocopy_safe=True)

PuBuGn=['#FFF7FB', '#F6EFF7', '#ECE2F0', '#D0D1E6', '#BDC9E1', '#A6BDDB', '#67A9CF', '#3690C0', '#1C9099', '#02818A', '#016C59', '#016450', '#014636']
PuBuGn9=Brew('sequential', sequential_from_scheme(PuBuGn, 9), 'PuBuGn', colorblind_safe=True)
PuBuGn8=Brew('sequential', sequential_from_scheme(PuBuGn, 8), 'PuBuGn', colorblind_safe=True)
PuBuGn7=Brew('sequential', sequential_from_scheme(PuBuGn, 7), 'PuBuGn', colorblind_safe=True)
PuBuGn6=Brew('sequential', sequential_from_scheme(PuBuGn, 6), 'PuBuGn', colorblind_safe=True)
PuBuGn5=Brew('sequential', sequential_from_scheme(PuBuGn, 5), 'PuBuGn', colorblind_safe=True)
PuBuGn4=Brew('sequential', sequential_from_scheme(PuBuGn, 4), 'PuBuGn', colorblind_safe=True)
PuBuGn3=Brew('sequential', sequential_from_scheme(PuBuGn, 3), 'PuBuGn', colorblind_safe=True, print_safe=True, photocopy_safe=True)

PuRd=['#F7F4F9', 'F1EEF6', '#E7E1EF', '#D7B5D8', '#D4B9DA', '#C994C7', '#DF65B0', '#E7298A', '#DD1C77', '#CE1256', '#980043', '#91003F', '#67001F'] 
PuRd9=Brew('sequential', sequential_from_scheme(PuRd, 9), 'PuRd', colorblind_safe=True)
PuRd8=Brew('sequential', sequential_from_scheme(PuRd, 8), 'PuRd', colorblind_safe=True)
PuRd7=Brew('sequential', sequential_from_scheme(PuRd, 7), 'PuRd', colorblind_safe=True)
PuRd6=Brew('sequential', sequential_from_scheme(PuRd, 6), 'PuRd', colorblind_safe=True)
PuRd5=Brew('sequential', sequential_from_scheme(PuRd, 5), 'PuRd', colorblind_safe=True, print_safe=True)
PuRd4=Brew('sequential', sequential_from_scheme(PuRd, 4), 'PuRd', colorblind_safe=True, print_safe=True)
PuRd3=Brew('sequential', sequential_from_scheme(PuRd, 3), 'PuRd', colorblind_safe=True, print_safe=True, photocopy_safe=True)

RdPu=['#FFF7F3', '#FEEBE2', '#FDE0DD', '#FCC5C0', '#FBB4B9', '#FA9FB5', '#F768A1', '#DD3497', '#C51B8A', '#AE017E', '#7A0177', '#7A0177','#49006A']
RdPu9=Brew('sequential', sequential_from_scheme(RdPu, 9), 'RdPu', colorblind_safe=True)
RdPu8=Brew('sequential', sequential_from_scheme(RdPu, 8), 'RdPu', colorblind_safe=True)
RdPu7=Brew('sequential', sequential_from_scheme(RdPu, 7), 'RdPu', colorblind_safe=True)
RdPu6=Brew('sequential', sequential_from_scheme(RdPu, 6), 'RdPu', colorblind_safe=True)
RdPu5=Brew('sequential', sequential_from_scheme(RdPu, 5), 'RdPu', colorblind_safe=True)
RdPu4=Brew('sequential', sequential_from_scheme(RdPu, 4), 'RdPu', colorblind_safe=True)
RdPu3=Brew('sequential', sequential_from_scheme(RdPu, 3), 'RdPu', colorblind_safe=True)

YlGn=['#FFFFE5', '#FFFFCC', '#F7FCB9', '#D9F0A3', '#C2E699', '#ADDD8E', '#78C679', '#41AB5D', '#31A354', '#238443', '#006837', '#005A32', '#004529']
YlGn9=Brew('sequential', sequential_from_scheme(YlGn, 9), 'YlGn', colorblind_safe=True)
YlGn8=Brew('sequential', sequential_from_scheme(YlGn, 8), 'YlGn', colorblind_safe=True)
YlGn7=Brew('sequential', sequential_from_scheme(YlGn, 7), 'YlGn', colorblind_safe=True)
YlGn6=Brew('sequential', sequential_from_scheme(YlGn, 6), 'YlGn', colorblind_safe=True)
YlGn5=Brew('sequential', sequential_from_scheme(YlGn, 5), 'YlGn', colorblind_safe=True)
YlGn4=Brew('sequential', sequential_from_scheme(YlGn, 4), 'YlGn', colorblind_safe=True)
YlGn3=Brew('sequential', sequential_from_scheme(YlGn, 3), 'YlGn', colorblind_safe=True, photocopy_safe=True, print_safe=True)

YlGnBu=['#FFFFD9', '#FFFFCC', '#EDF8B1', '#C7E9B4', '#A1DAB4', '#7FCDBB', '#41B6C4', '#1D91C0', '#2C7FB8', '#225EA8', '#253494', '#0C2C84', '#081D58']
YlGnBu9=Brew('sequential', sequential_from_scheme(YlGnBu, 9), 'YlGnBu', colorblind_safe=True)
YlGnBu8=Brew('sequential', sequential_from_scheme(YlGnBu, 8), 'YlGnBu', colorblind_safe=True)
YlGnBu7=Brew('sequential', sequential_from_scheme(YlGnBu, 7), 'YlGnBu', colorblind_safe=True)
YlGnBu6=Brew('sequential', sequential_from_scheme(YlGnBu, 6), 'YlGnBu', colorblind_safe=True)
YlGnBu5=Brew('sequential', sequential_from_scheme(YlGnBu, 5), 'YlGnBu', colorblind_safe=True, print_safe=True)
YlGnBu4=Brew('sequential', sequential_from_scheme(YlGnBu, 4), 'YlGnBu', colorblind_safe=True, print_safe=True)
YlGnBu3=Brew('sequential', sequential_from_scheme(YlGnBu, 3), 'YlGnBu', colorblind_safe=True, photocopy_safe=True, print_safe=True)

YlOrBr=['#FFFFE5', '#FFFFD4', '#FFF7BC', '#FEE391', '#FED98E', '#FEC44F', '#FE9929', '#EC7014', '#D95FOE', '#CC4C02', '#993404', '#82CD04', '#662506']
YlOrBr9=Brew('sequential', sequential_from_scheme(YlOrBr, 9), 'YlOrBr', colorblind_safe=True)
YlOrBr8=Brew('sequential', sequential_from_scheme(YlOrBr, 8), 'YlOrBr', colorblind_safe=True)
YlOrBr7=Brew('sequential', sequential_from_scheme(YlOrBr, 7), 'YlOrBr', colorblind_safe=True)
YlOrBr6=Brew('sequential', sequential_from_scheme(YlOrBr, 6), 'YlOrBr', colorblind_safe=True)
YlOrBr5=Brew('sequential', sequential_from_scheme(YlOrBr, 5), 'YlOrBr', colorblind_safe=True)
YlOrBr4=Brew('sequential', sequential_from_scheme(YlOrBr, 4), 'YlOrBr', colorblind_safe=True, print_safe=True)
YlOrBr3=Brew('sequential', sequential_from_scheme(YlOrBr, 3), 'YlOrBr', colorblind_safe=True, photocopy_safe=True,print_safe=True)

YlOrRd=['#FFFFCC', '#FFFFB2', '#FFEDA0', '#FED976', '#FECC5C', '#FEB24C', '#FD8D3C', '#FC4E2A', '#F03B20', '#E31A1C', '#BD0026', '#B10026', '#800026']
YlOrRd9=Brew('sequential', sequential_from_scheme(YlOrRd, 9), 'YlOrRd', colorblind_safe=True)
YlOrRd8=Brew('sequential', sequential_from_scheme(YlOrRd, 8), 'YlOrRd', colorblind_safe=True)
YlOrRd7=Brew('sequential', sequential_from_scheme(YlOrRd, 7), 'YlOrRd', colorblind_safe=True)
YlOrRd6=Brew('sequential', sequential_from_scheme(YlOrRd, 6), 'YlOrRd', colorblind_safe=True)
YlOrRd5=Brew('sequential', sequential_from_scheme(YlOrRd, 5), 'YlOrRd', colorblind_safe=True)
YlOrRd4=Brew('sequential', sequential_from_scheme(YlOrRd, 4), 'YlOrRd', colorblind_safe=True, print_safe=True)
YlOrRd3=Brew('sequential', sequential_from_scheme(YlOrRd, 3), 'YlOrRd', colorblind_safe=True, photocopy_safe=True, print_safe=True)

Blues=['#F7FBFF', '#', '#DEEBF7', '#C6DBEF', '#BDD7E7', '#9ECAE1', '#6BAED6', '#4292C6', '#3182BD', '#2171B5', '#08519C', '#084594', '#08306B']
Blues9=Brew('sequential', sequential_from_scheme(Blues, 9), 'Blues', colorblind_safe=True)
Blues8=Brew('sequential', sequential_from_scheme(Blues, 8), 'Blues', colorblind_safe=True)
Blues7=Brew('sequential', sequential_from_scheme(Blues, 7), 'Blues', colorblind_safe=True)
Blues6=Brew('sequential', sequential_from_scheme(Blues, 6), 'Blues', colorblind_safe=True)
Blues5=Brew('sequential', sequential_from_scheme(Blues, 5), 'Blues', colorblind_safe=True)
Blues4=Brew('sequential', sequential_from_scheme(Blues, 4), 'Blues', colorblind_safe=True)
Blues3=Brew('sequential', sequential_from_scheme(Blues, 3), 'Blues', colorblind_safe=True, photocopy_safe=True, print_safe=True)

Greens=['#F7FCF5', '#EDF8E9', '#E5F5E0', '#C7E9C0', '#BAE4B3', '#A2D99B', '#74C476', '#41AB5D', '#31A354', '#238B45', '#006D2C', '#005A32', '#00441B']
Greens9=Brew('sequential', sequential_from_scheme(Greens, 9), 'Greens', colorblind_safe=True)
Greens8=Brew('sequential', sequential_from_scheme(Greens, 8), 'Greens', colorblind_safe=True)
Greens7=Brew('sequential', sequential_from_scheme(Greens, 7), 'Greens', colorblind_safe=True)
Greens6=Brew('sequential', sequential_from_scheme(Greens, 6), 'Greens', colorblind_safe=True)
Greens5=Brew('sequential', sequential_from_scheme(Greens, 5), 'Greens', colorblind_safe=True)
Greens4=Brew('sequential', sequential_from_scheme(Greens, 4), 'Greens', colorblind_safe=True)
Greens3=Brew('sequential', sequential_from_scheme(Greens, 3), 'Greens', colorblind_safe=True, photocopy_safe=True, print_safe=True)

Greys=['#FFFFFF', '#F7F7F7', '#F0F0F0', '#D9D9D9', '#CCCCCC', '#BDBDBD', '#969696', '#737373', '#636363', '#525252', '#252525', '#252525', '#000000']
Greys9=Brew('sequential', sequential_from_scheme(Greys, 9), 'Greys', colorblind_safe=True)
Greys8=Brew('sequential', sequential_from_scheme(Greys, 8), 'Greys', colorblind_safe=True)
Greys7=Brew('sequential', sequential_from_scheme(Greys, 7), 'Greys', colorblind_safe=True)
Greys6=Brew('sequential', sequential_from_scheme(Greys, 6), 'Greys', colorblind_safe=True)
Greys5=Brew('sequential', sequential_from_scheme(Greys, 5), 'Greys', colorblind_safe=True)
Greys4=Brew('sequential', sequential_from_scheme(Greys, 4), 'Greys', colorblind_safe=True, print_safe=True)
Greys3=Brew('sequential', sequential_from_scheme(Greys, 3), 'Greys', colorblind_safe=True, photocopy_safe=True, print_safe=True)

Oranges=['#FFF5EB', '#', '#FEE6CE', '#FDD0A2', '#', '#FDAE6B', '#FD8D3C', '#F16913', '#','#D94801', '#A63603', '#8C2D04', '#7F2704']
Oranges9=Brew('sequential', sequential_from_scheme(Oranges, 9), 'Oranges', colorblind_safe=True)
Oranges8=Brew('sequential', sequential_from_scheme(Oranges, 8), 'Oranges', colorblind_safe=True)
Oranges7=Brew('sequential', sequential_from_scheme(Oranges, 7), 'Oranges', colorblind_safe=True)
Oranges6=Brew('sequential', sequential_from_scheme(Oranges, 6), 'Oranges', colorblind_safe=True)
Oranges5=Brew('sequential', sequential_from_scheme(Oranges, 5), 'Oranges', colorblind_safe=True)
Oranges4=Brew('sequential', sequential_from_scheme(Oranges, 4), 'Oranges', colorblind_safe=True)
Oranges3=Brew('sequential', sequential_from_scheme(Oranges, 3), 'Oranges', colorblind_safe=True, photocopy_safe=True, print_safe=True)

Purples=['#FCFBFD', '#F2F0F7', '#EFEDF5', '#DADAEB', '#CBC9E2', '#BCBDDC', '#9E9AC8', '#807DBA', '#756BB1', '#6A51A3', '#54278F', '#4A1486', '#3F007D']
Purples9=Brew('sequential', sequential_from_scheme(Purples, 9), 'Purples', colorblind_safe=True)
Purples8=Brew('sequential', sequential_from_scheme(Purples, 8), 'Purples', colorblind_safe=True)
Purples7=Brew('sequential', sequential_from_scheme(Purples, 7), 'Purples', colorblind_safe=True)
Purples6=Brew('sequential', sequential_from_scheme(Purples, 6), 'Purples', colorblind_safe=True)
Purples5=Brew('sequential', sequential_from_scheme(Purples, 5), 'Purples', colorblind_safe=True)
Purples4=Brew('sequential', sequential_from_scheme(Purples, 4), 'Purples', colorblind_safe=True)
Purples3=Brew('sequential', sequential_from_scheme(Purples, 3), 'Purples', colorblind_safe=True, photocopy_safe=True, print_safe=True)

Reds=['#FFF5F0', '#FEE5D9', '#FEE0D2', '#FCBBA1', '#FCAE91', '#FC9272', '#FB6A4A', '#EF3B2C', '#DE2D26', '#CB181D', '#A50F15', '#99000D', '#67000D']
Reds9=Brew('sequential', sequential_from_scheme(Reds, 9), 'Reds', colorblind_safe=True)
Reds8=Brew('sequential', sequential_from_scheme(Reds, 8), 'Reds', colorblind_safe=True)
Reds7=Brew('sequential', sequential_from_scheme(Reds, 7), 'Reds', colorblind_safe=True)
Reds6=Brew('sequential', sequential_from_scheme(Reds, 6), 'Reds', colorblind_safe=True)
Reds5=Brew('sequential', sequential_from_scheme(Reds, 5), 'Reds', colorblind_safe=True)
Reds4=Brew('sequential', sequential_from_scheme(Reds, 4), 'Reds', colorblind_safe=True)
Reds3=Brew('sequential', sequential_from_scheme(Reds, 3), 'Reds', colorblind_safe=True, photocopy_safe=True, print_safe=True)

Accent=['#7FC97F', '#BEAED4', '#FDC086', '#FFFF99', '#386CB0', '#F0027F', '#BF5B17', '#666666']
Accent8=Brew('qualitative', qualitative_from_scheme(Accent, 8), 'Accent')
Accent7=Brew('qualitative', qualitative_from_scheme(Accent, 7), 'Accent')
Accent6=Brew('qualitative', qualitative_from_scheme(Accent, 6), 'Accent')
Accent5=Brew('qualitative', qualitative_from_scheme(Accent, 5), 'Accent')
Accent4=Brew('qualitative', qualitative_from_scheme(Accent, 4), 'Accent', print_safe=True)
Accent3=Brew('qualitative', qualitative_from_scheme(Accent, 3), 'Accent', print_safe=True)

Dark2=['#1B9E77', '#D95F02', '#7570B3', '#E7298A', '#66A61E', '#E6AB02', '#A6761D', '#666666']
Dark2_8=Brew('qualitative', qualitative_from_scheme(Dark2, 8), 'Dark2', print_safe=True)
Dark2_7=Brew('qualitative', qualitative_from_scheme(Dark2, 7), 'Dark2', print_safe=True)
Dark2_6=Brew('qualitative', qualitative_from_scheme(Dark2, 6), 'Dark2', print_safe=True)
Dark2_5=Brew('qualitative', qualitative_from_scheme(Dark2, 5), 'Dark2', print_safe=True)
Dark2_4=Brew('qualitative', qualitative_from_scheme(Dark2, 4), 'Dark2', print_safe=True)
Dark2_3=Brew('qualitative', qualitative_from_scheme(Dark2, 3), 'Dark2',colorblind_safe=True, print_safe=True)

Paired=['#A6CEE3', '#1F78B4', '#B2DF8A', '#33A02C', '#FB9A99', '#E31A1C', '#FDBF6F', '#FF7F00', '#CAB2D6', '#6A3D9A', '#FFFF99']
Paired11=Brew('qualitative', qualitative_from_scheme(Paired, 11), 'Paired')
Paired10=Brew('qualitative', qualitative_from_scheme(Paired, 10), 'Paired')
Paired9=Brew('qualitative', qualitative_from_scheme(Paired, 9), 'Paired')
Paired8=Brew('qualitative', qualitative_from_scheme(Paired, 8), 'Paired')
Paired7=Brew('qualitative', qualitative_from_scheme(Paired, 7), 'Paired', print_safe=True)
Paired6=Brew('qualitative', qualitative_from_scheme(Paired, 6), 'Paired', print_safe=True)
Paired5=Brew('qualitative', qualitative_from_scheme(Paired, 5), 'Paired', print_safe=True)
Paired4=Brew('qualitative', qualitative_from_scheme(Paired, 4), 'Paired', colorblind_safe=True, print_safe=True)
Paired3=Brew('qualitative', qualitative_from_scheme(Paired, 3), 'Paired', colorblind_safe=True, print_safe=True)

Pastel1=['#FBB4AE', '#B3CDE3', '#CCEBC5', '#DECBE4', '#FED9A6', '#FFFFCC', '#E5D8BD', '#FDDAEC', '#F2F2F2']
Pastel1_9=Brew('qualitative', qualitative_from_scheme(Pastel1, 9), 'Pastel1')
Pastel1_8=Brew('qualitative', qualitative_from_scheme(Pastel1, 8), 'Pastel1')
Pastel1_7=Brew('qualitative', qualitative_from_scheme(Pastel1, 7), 'Pastel1')
Pastel1_6=Brew('qualitative', qualitative_from_scheme(Pastel1, 6), 'Pastel1')
Pastel1_5=Brew('qualitative', qualitative_from_scheme(Pastel1, 5), 'Pastel1')
Pastel1_4=Brew('qualitative', qualitative_from_scheme(Pastel1, 4), 'Pastel1')
Pastel1_3=Brew('qualitative', qualitative_from_scheme(Pastel1, 3), 'Pastel1')

Pastel2=['#B3E2CD', '#FDCDAC', '#CBD5E8', '#F4CAE4', '#E6F5C9', '#FFF2AE', '#F1E2CC', '#CCCCCC']
Pastel2_8=Brew('qualitative', qualitative_from_scheme(Pastel2, 8), 'Pastel2')
Pastel2_7=Brew('qualitative', qualitative_from_scheme(Pastel2, 7), 'Pastel2')
Pastel2_6=Brew('qualitative', qualitative_from_scheme(Pastel2, 6), 'Pastel2')
Pastel2_5=Brew('qualitative', qualitative_from_scheme(Pastel2, 5), 'Pastel2')
Pastel2_4=Brew('qualitative', qualitative_from_scheme(Pastel2, 4), 'Pastel2')
Pastel2_3=Brew('qualitative', qualitative_from_scheme(Pastel2, 3), 'Pastel2')

Set1=['#E41A1C', '#377EB8', '#4DAF4A', '#984EA3', '#FF7F00', '#FFFF33', '#A65628', '#F781BF', '#999999']
Set1_9=Brew('qualitative', qualitative_from_scheme(Set1, 9), 'Set1', print_safe=True)
Set1_8=Brew('qualitative', qualitative_from_scheme(Set1, 8), 'Set1', print_safe=True)
Set1_7=Brew('qualitative', qualitative_from_scheme(Set1, 7), 'Set1', print_safe=True)
Set1_6=Brew('qualitative', qualitative_from_scheme(Set1, 6), 'Set1', print_safe=True)
Set1_5=Brew('qualitative', qualitative_from_scheme(Set1, 5), 'Set1', print_safe=True)
Set1_4=Brew('qualitative', qualitative_from_scheme(Set1, 4), 'Set1', print_safe=True)
Set1_3=Brew('qualitative', qualitative_from_scheme(Set1, 3), 'Set1', print_safe=True)

Set2=['#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3', '#A6D854', '#FFD92F', '#E5C494', '#B3B3b3']
Set2_8=Brew('qualitative', qualitative_from_scheme(Set2, 8), 'Set2')
Set2_7=Brew('qualitative', qualitative_from_scheme(Set2, 7), 'Set2')
Set2_6=Brew('qualitative', qualitative_from_scheme(Set2, 6), 'Set2')
Set2_5=Brew('qualitative', qualitative_from_scheme(Set2, 5), 'Set2', print_safe=True)
Set2_4=Brew('qualitative', qualitative_from_scheme(Set2, 4), 'Set2', print_safe=True)
Set2_3=Brew('qualitative', qualitative_from_scheme(Set2, 3), 'Set2', colorblind_safe=True, print_safe=True)

Set3=['#8DD3C7', '#FFFFB3', '#BEBADA', '#FB8072', '#80B1D3', '#FDB462', '#B3DE69', '#FCCDE5', '#D9D9D9', '#BC80BD', '#CCEBC5', '#FFED6F']
Set3_12=Brew('qualitative', qualitative_from_scheme(Set3, 12), 'Set3')
Set3_11=Brew('qualitative', qualitative_from_scheme(Set3, 11), 'Set3')
Set3_10=Brew('qualitative', qualitative_from_scheme(Set3, 10), 'Set3')
Set3_9=Brew('qualitative', qualitative_from_scheme(Set3, 9), 'Set3')
Set3_8=Brew('qualitative', qualitative_from_scheme(Set3, 8), 'Set3', print_safe=True)
Set3_7=Brew('qualitative', qualitative_from_scheme(Set3, 7), 'Set3', print_safe=True)
Set3_6=Brew('qualitative', qualitative_from_scheme(Set3, 6), 'Set3', print_safe=True)
Set3_5=Brew('qualitative', qualitative_from_scheme(Set3, 5), 'Set3', print_safe=True)
Set3_4=Brew('qualitative', qualitative_from_scheme(Set3, 4), 'Set3', print_safe=True)
Set3_3=Brew('qualitative', qualitative_from_scheme(Set3, 3), 'Set3', photocopy_safe=True,print_safe=True)

BrBG=['#543005', '#8C510A', '#A6611A', '#BF812D', '#D8B365', '#DFC27D', '#F6E8C3', '#F5F5F5', '#C7EAE5', '#80CDC1', '#5AB4AC', '#35978F', '#018571', '#01665E', '#003C30']
BrBG11=Brew('diverging', diverging_from_scheme(BrBG, 11), 'BrBG', colorblind_safe=True)
BrBG10=Brew('diverging', diverging_from_scheme(BrBG, 10), 'BrBG', colorblind_safe=True)
BrBG9=Brew('diverging', diverging_from_scheme(BrBG, 9), 'BrBG', colorblind_safe=True)
BrBG8=Brew('diverging', diverging_from_scheme(BrBG, 8), 'BrBG', colorblind_safe=True)
BrBG7=Brew('diverging', diverging_from_scheme(BrBG, 7), 'BrBG', colorblind_safe=True)
BrBG6=Brew('diverging', diverging_from_scheme(BrBG, 6), 'BrBG', colorblind_safe=True, print_safe=True)
BrBG5=Brew('diverging', diverging_from_scheme(BrBG, 5), 'BrBG', colorblind_safe=True, print_safe=True)
BrBG4=Brew('diverging', diverging_from_scheme(BrBG, 4), 'BrBG', colorblind_safe=True, print_safe=True)
BrBG3=Brew('diverging', diverging_from_scheme(BrBG, 3), 'BrBG', colorblind_safe=True, print_safe=True)

PiYG=['#8E0152', '#C51B7D', '#D01C8B', '#DE77AE', '#E9A3C9', '#F1B6DA', '#FDE0EF', '#F7F7F7', '#E6F5D0', '#B8E186', '#A1D76A', '#7FBC41', '#4DAC26', '#4D9221', '#276419']
PiYG11=Brew('diverging', diverging_from_scheme(PiYG, 11), 'PiYG', colorblind_safe=True)
PiYG10=Brew('diverging', diverging_from_scheme(PiYG, 10), 'PiYG', colorblind_safe=True)
PiYG9=Brew('diverging', diverging_from_scheme(PiYG, 9), 'PiYG', colorblind_safe=True)
PiYG8=Brew('diverging', diverging_from_scheme(PiYG, 8), 'PiYG', colorblind_safe=True)
PiYG7=Brew('diverging', diverging_from_scheme(PiYG, 7), 'PiYG', colorblind_safe=True)
PiYG6=Brew('diverging', diverging_from_scheme(PiYG, 6), 'PiYG', colorblind_safe=True)
PiYG5=Brew('diverging', diverging_from_scheme(PiYG, 5), 'PiYG', colorblind_safe=True)
PiYG4=Brew('diverging', diverging_from_scheme(PiYG, 4), 'PiYG', colorblind_safe=True, print_safe=True)
PiYG3=Brew('diverging', diverging_from_scheme(PiYG, 3), 'PiYG', colorblind_safe=True, print_safe=True)

PRGn=['#40004B', '#762A83', '#7B3294', '#9970AB', '#AF8DC3', '#C2A5CF', '#E7D4E8', '#F7F7F7', '#D9F0D3', '#A6DBA0', '#7FBF7B', '#5AAE61', '#008837', '#1B7837','#00441B']
PrGn11=Brew('diverging', diverging_from_scheme(PRGn, 11), 'PRGn', colorblind_safe=True)
PrGn10=Brew('diverging', diverging_from_scheme(PRGn, 10), 'PRGn', colorblind_safe=True)
PrGn9=Brew('diverging', diverging_from_scheme(PRGn, 9), 'PRGn', colorblind_safe=True)
PrGn8=Brew('diverging', diverging_from_scheme(PRGn, 8), 'PRGn', colorblind_safe=True)
PrGn7=Brew('diverging', diverging_from_scheme(PRGn, 7), 'PRGn', colorblind_safe=True)
PrGn6=Brew('diverging', diverging_from_scheme(PRGn, 6), 'PRGn', colorblind_safe=True, print_safe=True)
PrGn5=Brew('diverging', diverging_from_scheme(PRGn, 5), 'PRGn', colorblind_safe=True, print_safe=True)
PrGn4=Brew('diverging', diverging_from_scheme(PRGn, 4), 'PRGn', colorblind_safe=True, print_safe=True)
PrGn3=Brew('diverging', diverging_from_scheme(PRGn, 3), 'PRGn', colorblind_safe=True, print_safe=True)

PuOr=['#7F3B08', '#B35806', '#E66101', '#E08214', '#F1A340', '#FDB863', '#FEE0B6', '#F7F7F7', '#D8DAEB', '#B2ABD2', '#998EC3', '#8073AC', '#5E3C99', '#542788', '#2D004B']
PuOr11=Brew('diverging', diverging_from_scheme(PuOr, 11), 'PuOr', colorblind_safe=True)
PuOr10=Brew('diverging', diverging_from_scheme(PuOr, 10), 'PuOr', colorblind_safe=True)
PuOr9=Brew('diverging', diverging_from_scheme(PuOr, 9), 'PuOr', colorblind_safe=True)
PuOr8=Brew('diverging', diverging_from_scheme(PuOr, 8), 'PuOr', colorblind_safe=True)
PuOr7=Brew('diverging', diverging_from_scheme(PuOr, 7), 'PuOr', colorblind_safe=True)
PuOr6=Brew('diverging', diverging_from_scheme(PuOr, 6), 'PuOr', colorblind_safe=True)
PuOr5=Brew('diverging', diverging_from_scheme(PuOr, 5), 'PuOr', colorblind_safe=True)
PuOr4=Brew('diverging', diverging_from_scheme(PuOr, 4), 'PuOr', colorblind_safe=True, photocopy_safe=True, print_safe=True)
PuOr3=Brew('diverging', diverging_from_scheme(PuOr, 3), 'PuOr', colorblind_safe=True, photocopy_safe=True, print_safe=True)

RdBu=['#67001F', '#B2182B', '#CA0020', '#D6604D', '#EF8A62', '#F4A582', '#FDDBC7', '#F7F7F7', '#D1E5F0', '#92C5DE', '#67A9CF', '#4393C3', '#0571B0', '#2166AC', '#053061']
RdBu11=Brew('diverging', diverging_from_scheme(RdBu, 11), 'RdBu', colorblind_safe=True)
RdBu10=Brew('diverging', diverging_from_scheme(RdBu, 10), 'RdBu', colorblind_safe=True)
RdBu9=Brew('diverging', diverging_from_scheme(RdBu, 9), 'RdBu', colorblind_safe=True)
RdBu8=Brew('diverging', diverging_from_scheme(RdBu, 8), 'RdBu', colorblind_safe=True)
RdBu7=Brew('diverging', diverging_from_scheme(RdBu, 7), 'RdBu', colorblind_safe=True)
RdBu6=Brew('diverging', diverging_from_scheme(RdBu, 6), 'RdBu', colorblind_safe=True, print_safe=True)
RdBu5=Brew('diverging', diverging_from_scheme(RdBu, 5), 'RdBu', colorblind_safe=True, print_safe=True)
RdBu4=Brew('diverging', diverging_from_scheme(RdBu, 4), 'RdBu', colorblind_safe=True, print_safe=True)
RdBu3=Brew('diverging', diverging_from_scheme(RdBu, 3), 'RdBu', colorblind_safe=True, print_safe=True)

RdGy=['#67001F', '#B2182B', '#CA0020', '#D6604D', '#EF8A62', '#F4A582', '#FDDBC7', '#FFFFFF', '#E0E0E0', '#BABABA', '#999999', '#878787', '#404040', '#4D4D4D', '#1A1A1A']
RdGy11=Brew('diverging', diverging_from_scheme(RdGy, 11), 'RdGy', colorblind_safe=True)
RdGy10=Brew('diverging', diverging_from_scheme(RdGy, 10), 'RdGy', colorblind_safe=True)
RdGy9=Brew('diverging', diverging_from_scheme(RdGy, 9), 'RdGy', colorblind_safe=True)
RdGy8=Brew('diverging', diverging_from_scheme(RdGy, 8), 'RdGy', colorblind_safe=True)
RdGy7=Brew('diverging', diverging_from_scheme(RdGy, 7), 'RdGy', colorblind_safe=True)
RdGy6=Brew('diverging', diverging_from_scheme(RdGy, 6), 'RdGy', colorblind_safe=True)
RdGy5=Brew('diverging', diverging_from_scheme(RdGy, 5), 'RdGy', colorblind_safe=True, print_safe=True)
RdGy4=Brew('diverging', diverging_from_scheme(RdGy, 4), 'RdGy', colorblind_safe=True, print_safe=True)
RdGy3=Brew('diverging', diverging_from_scheme(RdGy, 3), 'RdGy', colorblind_safe=True, print_safe=True)

RdYlBu=['#A50026', '#D73027', '#D7191C', '#F46D43', '#FC8D59', '#FDAE61', '#FEE090', '#FFFFBF', '#E0F3F8', '#ABD9E9', '#91BFDB', '#74ADD1', '#2C7BB6', '#4575B4','#313695']
RdYlBu11=Brew('diverging', diverging_from_scheme(RdYlBu, 11), 'RdYlBu', colorblind_safe=True)
RdYlBu10=Brew('diverging', diverging_from_scheme(RdYlBu, 10), 'RdYlBu', colorblind_safe=True)
RdYlBu9=Brew('diverging', diverging_from_scheme(RdYlBu, 9), 'RdYlBu', colorblind_safe=True)
RdYlBu8=Brew('diverging', diverging_from_scheme(RdYlBu, 8), 'RdYlBu', colorblind_safe=True)
RdYlBu7=Brew('diverging', diverging_from_scheme(RdYlBu, 7), 'RdYlBu', colorblind_safe=True)
RdYlBu6=Brew('diverging', diverging_from_scheme(RdYlBu, 6), 'RdYlBu', colorblind_safe=True, print_safe=True)
RdYlBu5=Brew('diverging', diverging_from_scheme(RdYlBu, 5), 'RdYlBu', colorblind_safe=True, print_safe=True)
RdYlBu4=Brew('diverging', diverging_from_scheme(RdYlBu, 4), 'RdYlBu', colorblind_safe=True, print_safe=True)
RdYlBu3=Brew('diverging', diverging_from_scheme(RdYlBu, 3), 'RdYlBu', colorblind_safe=True, print_safe=True)

RdYlGn=['#A50026', '#D73027', '#D7191C', '#F46D43', '#FC8D59', '#FDAE61', '#FEE090', '#FFFFBF', '#D9EF8B', '#A6D96A', '#91CF60', '#66BD63', '#1A9641', '#1A9850', '#006837']
RdYlGn11=Brew('diverging', diverging_from_scheme(RdYlGn, 11), 'RdYlGn')
RdYlGn10=Brew('diverging', diverging_from_scheme(RdYlGn, 10), 'RdYlGn')
RdYlGn9=Brew('diverging', diverging_from_scheme(RdYlGn, 9), 'RdYlGn')
RdYlGn8=Brew('diverging', diverging_from_scheme(RdYlGn, 8), 'RdYlGn')
RdYlGn7=Brew('diverging', diverging_from_scheme(RdYlGn, 7), 'RdYlGn')
RdYlGn6=Brew('diverging', diverging_from_scheme(RdYlGn, 6), 'RdYlGn')
RdYlGn5=Brew('diverging', diverging_from_scheme(RdYlGn, 5), 'RdYlGn', print_safe=True)
RdYlGn4=Brew('diverging', diverging_from_scheme(RdYlGn, 4), 'RdYlGn', print_safe=True)
RdYlGn3=Brew('diverging', diverging_from_scheme(RdYlGn, 3), 'RdYlGn', print_safe=True)

Spectral=['#9E0142', '#D53E4F', '#D7191C', '#F46D43', '#FC8D59', '#FDAE61', '#FEE08B', '#FFFFBF', '#E6F598', '#ABDDA4', '#99D594', '#66C2A5', '#2B83BA', '#32888D', '#5E4FA2']
Spectral11=Brew('diverging', diverging_from_scheme(Spectral, 11), 'Spectral')
Spectral10=Brew('diverging', diverging_from_scheme(Spectral, 10), 'Spectral')
Spectral9=Brew('diverging', diverging_from_scheme(Spectral, 9), 'Spectral')
Spectral8=Brew('diverging', diverging_from_scheme(Spectral, 8), 'Spectral')
Spectral7=Brew('diverging', diverging_from_scheme(Spectral, 7), 'Spectral')
Spectral6=Brew('diverging', diverging_from_scheme(Spectral, 6), 'Spectral')
Spectral5=Brew('diverging', diverging_from_scheme(Spectral, 5), 'Spectral', print_safe=True, photocopy_safe=True)
Spectral4=Brew('diverging', diverging_from_scheme(Spectral, 4), 'Spectral', print_safe=True, photocopy_safe=True)
Spectral3=Brew('diverging', diverging_from_scheme(Spectral, 3), 'Spectral', print_safe=True, photocopy_safe=True)

brews=[
    BuGn3, BuGn4, BuGn5, BuGn6, BuGn7, BuGn8, BuGn9, 
    BuPu3, BuPu4, BuPu5, BuPu6, BuPu7, BuPu8, BuPu9, 
    GnBu3, GnBu4, GnBu5, GnBu6, GnBu7, GnBu8, GnBu9, 
    OrRd3, OrRd4, OrRd5, OrRd6, OrRd7, OrRd8, OrRd9, 
    PuBu3, PuBu4, PuBu5, PuBu6, PuBu7, PuBu8, PuBu9, 
    PuBuGn3, PuBuGn4, PuBuGn5, PuBuGn6, PuBuGn7, PuBuGn8, PuBuGn9,
    PuRd3, PuRd4, PuRd5, PuRd6, PuRd7, PuRd8, PuRd9,
    RdPu3, RdPu4, RdPu5, RdPu6, RdPu7, RdPu8, RdPu9,
    YlGn3, YlGn4, YlGn5, YlGn6, YlGn7, YlGn8, YlGn9, 
    YlGnBu3, YlGnBu4, YlGnBu5, YlGnBu6, YlGnBu7, YlGnBu8, YlGnBu9,
    YlOrBr3, YlOrBr4, YlOrBr5, YlOrBr6, YlOrBr7, YlOrBr8, YlOrBr9,
    YlOrRd3, YlOrRd4, YlOrRd5, YlOrRd6, YlOrRd7, YlOrRd8, YlOrRd9,
    Blues3, Blues4, Blues5, Blues6, Blues7, Blues8, Blues9,
    Greens3, Greens4, Greens5, Greens6, Greens7, Greens8, Greens9,
    Greys3, Greys4, Greys5, Greys6, Greys7, Greys8, Greys9,
    Oranges3, Oranges4, Oranges5, Oranges6, Oranges7, Oranges8, Oranges9,
    Purples3, Purples4, Purples5, Purples6, Purples7, Purples8, Purples9,
    Reds3, Reds4, Reds5, Reds6, Reds7, Reds8, Reds9, 

    Accent3, Accent4, Accent5, Accent6, Accent7, Accent8, 
    Dark2_3, Dark2_4, Dark2_5, Dark2_6, Dark2_7, Dark2_8, 
    Paired3, Paired4, Paired5, Paired6, Paired7, Paired8, Paired9, Paired10, Paired11,
    Pastel1_3, Pastel1_4, Pastel1_5, Pastel1_6, Pastel1_7, Pastel1_8, Pastel1_9,
    Pastel2_3, Pastel2_4, Pastel2_5, Pastel2_6, Pastel2_7, Pastel2_8,
    Set1_3, Set1_4, Set1_5, Set1_6, Set1_7, Set1_8, Set1_9, 
    Set2_3, Set2_4, Set2_5, Set2_6, Set2_7, Set2_8, 
    Set3_3, Set3_4, Set3_5, Set3_6, Set3_7, Set3_8, Set3_9, Set3_10, Set3_11, Set3_12,

    BrBG3, BrBG4, BrBG5, BrBG6, BrBG7, BrBG8, BrBG9, BrBG10, BrBG11,
    PiYG3, PiYG4, PiYG5, PiYG6, PiYG7, PiYG8, PiYG9, PiYG10, PiYG11,
    PrGn3, PrGn4, PrGn5, PrGn6, PrGn7, PrGn8, PrGn9, PrGn10, PrGn11,
    PuOr3, PuOr4, PuOr5, PuOr6, PuOr7, PuOr8, PuOr9, PuOr10, PuOr11,
    RdBu3, RdBu4, RdBu5, RdBu6, RdBu7, RdBu8, RdBu9, RdBu10, RdBu11,
    RdGy3, RdGy4, RdGy5, RdGy6, RdGy7, RdGy8, RdGy9, RdGy10, RdGy11,
    RdYlBu3, RdYlBu4, RdYlBu5, RdYlBu6, RdYlBu7, RdYlBu8, RdYlBu9, RdYlBu10, RdYlBu11,
    RdYlGn3, RdYlGn4, RdYlGn5, RdYlGn6, RdYlGn7, RdYlGn8, RdYlGn9, RdYlGn10, RdYlGn11,
    Spectral3, Spectral4, Spectral5, Spectral6, Spectral7, Spectral8, Spectral9, Spectral10, Spectral11
] 

class BrewSelector:
    
    def add_brew(self, brew):
        self.brews[brew.datatype][brew.num_bins][brew.scheme]=brew
    
    def add_brews(self,brew_iterable):
        for brew in brew_iterable:
            self.add_brew(brew)

    def __init__(self, empty=False):
        self.brews={'sequential': defaultdict(dict), 'diverging': defaultdict(dict), 'qualitative': defaultdict(dict)}
        if not empty:
            self.add_brews(brews)

    def get_brew(self, datatype, num_bins, scheme):
        try:
            return self.brews[datatype][num_bins][scheme]
        except KeyError:
            raise Exception("There is no such Brew, sorry.")
    
    def list_schemes(self, datatype, num_bins, colorblind_safe=False, photocopy_safe=False, print_safe=False):
        try:
            return tuple(brew.scheme for brew in self.brews[datatype][num_bins].values() if (not colorblind_safe or brew.colorblind_safe) and (not photocopy_safe or brew.photocopy_safe) and (not print_safe or brew.print_safe))
        except KeyError:
            raise Exception("There are no Brews for that many bins for that datatype")