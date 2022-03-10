# 🧪 TestMaster
My personnal master testsuite in python, only for fonctionnal tests.
## Small setup
Use python3.  
Install all modules with:  
```console
pip install -r requirements.txt
```  
  
To add tests use `tests.yaml` file. Find the synthax in wiki.
Example of `tests.yaml` file:
``` yaml
- name: "Basic echo tests"
  baseInput: "echo"
  tests:
    - name: "hello_test"
      input: "hello"
      exp_out: "hello\n"
    - name: "good_test"
      input: "good"
      exp_out: "good\n"

- name: "Basic cat from files"
  baseInput: "cat"
  tests_from_folder: "./tests/"
```
 
`testsuite.py` can take arguments. To see all available argument got to wiki or :   
```console
python3 testsuite.py --help 
```
  
Enjoy !  
  
   

![alt text](https://github.com/Louisp78/TestMaster/blob/main/screen.png?raw=true)
