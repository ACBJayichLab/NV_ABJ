from sumitomo_f70 import SumitomoF70

with SumitomoF70(com_port='COM6xxx') as f70:
    # Insert commands here (full list in docs)
    # For example:
    t1, t2, t3, t4 = f70.read_all_temperatures()

print(t1,t2,t3,t4)