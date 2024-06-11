import sys
import subprocess


def running_program(args):
	# Turn Off Network Manager
	subprocess.run(["sudo", "systemctl", "stop", "network-manager"])   
	# Refresh Mininet-WiFi
	subprocess.run(["sudo", "mn", "-c"])    
	# Execute the appropriate script based on the routing protocols
	if '-sdvn' in args:
		print("-"*30 + "SDVN OPENFLOW IS RUNNING" + "-"*30)  
		subprocess.run(["sudo", "python", "bi_sdvn.py"])
	elif '-adhoc' in args:
		print("-"*30 + "ADHOC MESH IS RUNNING" + "-"*30)
		subprocess.run(["sudo", "python", "bi_adhoc.py"])
	elif '-sdvn_tpa' in args:
		print("-"*30 + "SDVN OPENFLOW TPA IS RUNNING" + "-"*30)
		subprocess.run(["sudo", "python", "bi_integration.py"])
        
        
if __name__ == "__main__":
    running_program(sys.argv)
