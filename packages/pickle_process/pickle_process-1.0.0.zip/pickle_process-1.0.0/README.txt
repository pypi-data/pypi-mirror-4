This package is capable of

1) Sending a data to a pickled state
2) Unpickling the pickled data

There are two seperate functions

pickle_data(val1,val2) - Used to pickle the data

-->val1 - Data to be pickled (required)
-->Val2 - name of the file to be written to (Optional)

unpickle_data(val1,val2,val3) - used to unpickle the pickled data

-->val1 - name of the pickled file (Required)
-->val2	- Set it to 'True' if the output has to be written to a file (optional). Default is 'False'(shell output) 
-->Val3	- name of the file to be written to (optional)