#┌──────────────────────────────────────────────────┐
#│ MAKEFILE MAIN EXECUTABLE                         │
#│                                                  │
#│ (C) T O'BRIEN 2011   ID: 1552317   UPI:tobr017   │
#│                                                  │
#└──────────────────────────────────────────────────┘

all:

clean: 

	cd databases; rm -f login_credentials.db statusfeed.db images.db; touch images.db; touch login_credentials.db; touch statusfeed.db;

databases:
	
	./init_script.py


