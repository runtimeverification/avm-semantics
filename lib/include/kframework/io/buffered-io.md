Buffered IO
===========

```k
module BUFFERED-IO
  imports INT
  imports STRING
  imports K-EQUAL
  imports K-IO

  syntax KItem ::= readFromFile(String)
                 | writeToFile(String, String)
                 | openR(IOInt)
                 | openW(IOInt)
                 | buffer(IOString)
                 | returnW(K)
                 | closing(K)

  syntax Int ::= "CHUNKSIZE" [macro]
  // -------------------------------
  rule CHUNKSIZE => 100
```

### Buffered IO Configuration

```k
  configuration
    <bufferedIO>
      <bio-op>     .K </bio-op>     // file IO operation, or output upon completion or error
      <bio-file>   "" </bio-file>   // file name (path) to be read from or written to
      <bio-fd>     -1 </bio-fd>     // file descriptor, or -1 for uninitialized, or < -1 for error
      <bio-buffer> "" </bio-buffer> // internal read buffer
      <bio-error>  "" </bio-error>  // read/write error message
    </bufferedIO>
```

### Reading from file

```k
  // Open the input file for reading
  rule <bio-op> readFromFile(FILE) => openR(#open(FILE)) </bio-op>
       <bio-file> _ => FILE </bio-file>

  // successfully opened the file, begin reading
  rule <bio-op> openR(FD:Int) => buffer(#read(FD, CHUNKSIZE)) </bio-op>
       <bio-fd> _ => FD </bio-fd>

  // error openning file for reading, report an error
  rule <bio-op> openR(E:IOError) => E </bio-op>
       <bio-file> FILE </bio-file>
       <bio-fd> _ => -2 </bio-fd>
       <bio-error> _ => "IOError: error openning input file: " +String FILE </bio-error>

  // a chunk of file was read successfully, move on to the next chunk
  rule <bio-op> buffer(S:String) => buffer(#read(FD, CHUNKSIZE)) </bio-op>
       <bio-fd> FD </bio-fd>
       <bio-buffer> IN => IN +String S </bio-buffer>
    requires S =/=K ""

  // error whiile reading from file, report the error
  rule <bio-op> buffer(E:IOError) => E </bio-op>
       <bio-file> FILE </bio-file>
       <bio-fd> _ => -3 </bio-fd>
       <bio-error> _ => "IOError: error reading from file: " +String FILE </bio-error>

  // no more input to be read, close the file
  rule <bio-op> buffer("") => closing(#close(FD)) </bio-op>
       <bio-fd> FD </bio-fd>

```

### Writing to file

```k
  // open the output file for writing
  rule <bio-op> writeToFile(FILE, S) => openW(#open(FILE, "w+")) </bio-op>
       <bio-file> _ => FILE </bio-file>
       <bio-buffer> _ => S </bio-buffer>

  // successfully opened the file, begin writing
  rule <bio-op> openW(FD:Int) => returnW(#write(FD, S)) </bio-op>
       <bio-fd> _ => FD </bio-fd>
       <bio-buffer> S => "" </bio-buffer>

  // error openning the file, report the error
  rule <bio-op> openW(E:IOError) => E </bio-op>
       <bio-file> FILE </bio-file>
       <bio-fd> _ => -2 </bio-fd>
       <bio-buffer> _ => "" </bio-buffer>
       <bio-error> _ => "IOError: error openning output file: " +String FILE </bio-error>

  // successfully completed writing to file, close the file
  rule <bio-op> returnW(.K) => closing(#close(FD)) </bio-op>
       <bio-fd> FD </bio-fd>

  // error while writing to file, report the error
  rule <bio-op> returnW(E:IOError) => E </bio-op>
       <bio-file> FILE </bio-file>
       <bio-fd> _ => -4 </bio-fd>
       <bio-error> _ => "IOError: error writing to file: " +String FILE </bio-error>
```

### Finalizatioin

```k
  // successfully closed the file, return the read buffer
  // (or the empty string if the file was opened for writing)
  rule <bio-op> closing(.K) => IN </bio-op>
       <bio-file> _ => "" </bio-file>
       <bio-fd> _ => -1 </bio-fd>
       <bio-buffer> IN => "" </bio-buffer>

  // error closing the file, report the error
  rule <bio-op> closing(E:IOError) => E </bio-op>
       <bio-file> FILE </bio-file>
       <bio-fd> _ => -4 </bio-fd>
       <bio-error> _ => "IOError: error closing file: " +String FILE </bio-error>
endmodule

```
