/* run with
 * dtrace -q -s latency_stats.d -c "command to process" class_name
 */
objc$target:$1::entry
{
    self->entry_time = timestamp;
}

objc$target:$1::return
/self->entry_time/
{
    this->delta_time = timestamp - self->entry_time;
    //printf ("%d %s %d ns\n", walltimestamp, probefunc, this->delta_time);
    @summation[probefunc] = sum(this->delta_time);
    @average[probefunc] = avg(this->delta_time);
    @maximum[probefunc] = max(this->delta_time);
    @minimum[probefunc] = min(this->delta_time);
    self->entry_time = 0;
}

dtrace:::END
{
    printf("\n-----------------Summation-----------------\n");
    printa(@summation[probefunc]);
    printf("\n-----------------Average-----------------\n");
    printa(@average[probefunc]);
    printf("\n-----------------Maximum-----------------\n");
    printa(@maximum[probefunc]);
    printf("\n-----------------Minimum-----------------\n");
    printa(@minimum[probefunc]);
}
