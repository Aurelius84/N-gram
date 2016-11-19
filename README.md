# N-gram
A project of N-gram model comparing FMM/BMM
Document:[http://fromwiz.com/share/s/229tNZ0vF4ql2YIr3G36BZnV0BIsSy26W4VN2Ih4fd3w_Rj0](http://fromwiz.com/share/s/229tNZ0vF4ql2YIr3G36BZnV0BIsSy26W4VN2Ih4fd3w_Rj0)

### Usage
Firstly, you should download the data '199801.txt' from Internet and put it in the project dir.
Use as followed:
```
python statistic.py
```
And you will get result like this:
```
successfully to split corpus by train = 0.900000 test = 0.100000
the total number of words is:53260
The total number of bigram is : 403121.
successfully witten-Bell smoothing! smooth_value:1.3372788850370981e-05
the total number of punction is:47
召回率为:0.962036929819092
准确率为:0.9401303935308096
F值为:0.950957517059212
```

### Todo
+ Ambiguity
+ OVV
+ Trigram
