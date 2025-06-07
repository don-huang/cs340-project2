# Reliable Streaming Transport Simulator

This project implements a simplified simulation of reliable data transmission over an unreliable network using UDP. It is adapted from a CS-340 course assignment and is written in Python.

## 📁 Project Structure

```
Project 2/
├── src/
│   ├── __init__.py            # Marks src as a package
│   ├── streamer.py            # Your implementation of the Streamer class
│   ├── lossy_socket.py        # Provided socket layer simulating unreliable network
├── tests/
│   └── test_streamer.py       # Functional test driver for Part 1 and Part 2
├── environment.yml            # Conda environment specification
├── .gitignore
├── README.md
```

## 🚀 How to Run

### ✅ Environment Setup

If you're using VS Code, you can configure the Python interpreter for this project
by creating a `.vscode/settings.json` file like this:

```json
{
  "python.defaultInterpreterPath": "/path/to/your/env/bin/python"
}
```

This ensures that VS Code uses the correct Conda environment for linting, debugging, and running the code.



Use Conda to create the environment:

```bash
conda env create -f environment.yml
conda activate cs340-project2
```

### ✅ Running the Test

Open two terminals in the project root:

**Terminal 1:**
```bash
python tests/test_streamer.py 8000 8001 1
```

**Terminal 2:**
```bash
python tests/test_streamer.py 8000 8001 2
```

You should see messages indicating successful message sending and receiving.

## 🧠 Files Overview

- `lossy_socket.py`: Simulates packet loss, corruption, and delay.
- `streamer.py`: Your implementation of reliable UDP-based transport.
- `test_streamer.py`: Orchestrates message sending/receiving between two simulated hosts and validates correctness.

## ✅ Current Status

- ✅ Part 0: Initial setup and raw send/receive tested
- ✅ Part 1: Chunking implemented for large UDP messages
- ⏳ Part 2+: To be implemented (reordering, ACKs, retransmission...)

## 📦 Dependencies

All required packages are in `environment.yml`. No external libraries beyond Python standard library are required.

## 🧑‍💻 Author

Adapted by Don Huang, based on code from Prof. Steve Tarzia (Northwestern University CS-340).
