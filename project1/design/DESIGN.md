# Design Documentation

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
- [Design Documentation](#design-documentation)
  - [📑 Table of Contents](#-table-of-contents)
  - [🧩 Introduction](#-introduction)
  - [🧭 Class Diagram](#-class-diagram)
  - [💡 Design Decisions](#-design-decisions)

---

## 🧩 Introduction
This document describes the design and structure of the **Discrete Event Simulation Project**.  
It outlines the architecture, major components, and how events are processed within the system.

## 🧭 Class Diagram
The following diagram illustrates the relationships between main components:

![Class Diagram](class_diagram.png)

> *Figure 1. Class diagram of the discrete event simulation system.*

---

## 💡 Design Decisions
Some of the key design choices include:
- Using **object-oriented principles** to encapsulate simulation logic.  
- Employing **discrete event scheduling** to model time-based behavior accurately.  
- Ensuring **modular structure** to allow future expansion or replacement of distribution models.  
- Supporting **different runtime modes** (slow, fast with messages, fast silent).

---


© 2025 University of Costa Rica. All rights reserved.  
Licensed under CC BY 4.0.