# Run inside Mininet CLI:
h1 python3 -m http.server 80 &
h2 iperf3 -s &
h3 bash -c 'while true; do curl -s http://10.0.0.1 >/dev/null; sleep 0.5; done' &
h4 iperf3 -c 10.0.0.2 -t 600 -b 5M &
h5 bash -c 'while true; do curl -s http://10.0.0.1 >/dev/null; sleep 1; done' &
