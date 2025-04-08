#!/bin/bash
ssh -N -f -L 8001:dh-dgxh100-2.hpc.msoe.edu:8000 weberbw@dh-mgmt3.hpc.msoe.edu
echo "Tunnel to LLaMA 3.3 started on http://localhost:8001"
