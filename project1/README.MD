# Discrete Event Simulation Project

**University of Costa Rica – School of Computer Science and Informatics**  
**Course:** CI-0130 Modeling and Optimization Methods  
**Project:** Simulation of a Message Processing System  
**Year:** 2025  
**Authors:** 
- Randall Araya C30569
- Samir Caro C31666
- Evan Chen C32200
- Melany Alfaro C30208
---

## 📑 Table of Contents
- [Discrete Event Simulation Project](#discrete-event-simulation-project)
  - [📑 Table of Contents](#-table-of-contents)
  - [🧩 Project Overview](#-project-overview)
  - [💻 System Description](#-system-description)
  - [⚙️ Simulation Details](#️-simulation-details)
  - [📈 Performance Metrics](#-performance-metrics)
  - [🗂️ Project Structure](#️-project-structure)
  - [🧭 Design Documentation](#-design-documentation)
  - [📘 User Manual](#-user-manual)
  - [📊 Results and Analysis](#-results-and-analysis)

---

## 🧩 Project Overview
This project consists of developing a **discrete event simulation** for a message processing network composed of three computers.  
The simulation models how messages are received, processed, and sent within the system, including delays, queue handling, and probabilistic message returns.

---

## 💻 System Description
The system simulates three computers with the following roles:

- **Computer 1**: Responsible for sending messages to their destination. It receives all processed messages from Computers 2 and 3 and may return some with errors for reprocessing.
- **Computer 2**: Receives external messages following an *exponential distribution* (mean of 15 seconds). Each message is processed for a *uniform time* between 5 and 10 seconds.  
  - 20% of messages sent to Computer 1 are returned for reprocessing.
- **Computer 3**: Receives external messages with *triangularly distributed* interarrival times (between 2 and 10 seconds).  
  - 75% of the messages are rejected permanently.  
  - Processing times follow the distribution:  
   $$
    f(x) = \frac{3x^2}{98}, \quad 3 \le x \le 5
  $$

  - Of the accepted messages, 50% of those sent to Computer 1 are returned for reprocessing.

---

## ⚙️ Simulation Details
At runtime, the user specifies:
1. Number of simulation runs.
2. Total simulated time (in seconds) per run.

The simulation supports three display modes:
- **Slow mode**: shows events and pauses between them.  
- **Fast mode with messages**: displays events without pauses.  
- **Fast silent mode**: no events shown, only final statistics.

Displayed information includes:
- System clock  
- Current event  
- Queue sizes  
- Processor states  
- Message counters for each computer  
- Total processing time  

---

## 📈 Performance Metrics
For each simulation run, the following are computed:

- **Average time a message spends in the system** (by case)  
- **Average waiting time in queues**  
- **System efficiency coefficients**  
- **Processor utilization times and percentages**  
- **Joint processing time among all processors**

After all runs, averages are presented for every metric.

Additionally, system performance is measured by the **average execution time** of a one-hour simulated run over 50 repetitions in fast mode.

---

## 🗂️ Project Structure
```
project_root/
├── src/                    # Source code
|   └── computer.py
|   └── event_types.py
|   └── master_computer.py
|   └── message.py
|   └── worker_computer.py
|   └── lazy_computer.py
|   └── simulator.py
|   └── stats_collector
├── design/                 # Design documents
│   └── README.md           # Design README (see below)
└── README.md               # This file
```

---

## 🧭 Design Documentation
The detailed design process, models, and diagrams are documented in the  
[Design README](design/README.md).

---

## 📘 User Manual
> _This section will be completed later._  
> It will describe the environment required to execute the program and step-by-step instructions for running the simulation.

---


## 📊 Results and Analysis
> _To be added once simulation results and system performance analyses are completed._

---

© 2025 University of Costa Rica. All rights reserved.  
Licensed under CC BY 4.0.
