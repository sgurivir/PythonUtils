import ProcessUtil

ProcessUtil.launch_process(full_path="/Applications/Firefox.app/Contents/MacOS/firefox",
                           kill_processes=["firefox"],
                           args="http://www.yahoo.com")

f_pid = ProcessUtil.launch_process(full_path="/Applications/Firefox.app/Contents/MacOS/firefox",
                           kill_processes=["firefox"],
                           args="http://www.google.com")

ProcessUtil.sample_process(f_pid, "/tmp/fpid.txt")