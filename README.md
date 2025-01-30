# Functions-Solver

https://github.com/user-attachments/assets/5a2c5183-90de-407f-86a5-5570c751aa4b

A powerful **mathematical functions solver** with a custom **parser and evaluator** built using **Pratt parsing**. This project efficiently handles various mathematical expressions, including **polynomials, trigonometric, exponential, and logarithmic functions**.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [How It Works: Pratt Parsing](#how-it-works-pratt-parsing)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

---

## **Features**

✔ **Custom Parser & Evaluator** → Uses **Pratt parsing** to efficiently parse and evaluate mathematical expressions.  
✔ **Supports Various Functions** → Solve **polynomial, trigonometric, exponential, and logarithmic** functions.  
✔ **Efficient & Extensible** → Designed for quick computations and easy expansion.  
✔ **Graphical User Interface** → Built using **PySide2** for an interactive experience.  
✔ **Visualization Support** → Uses **Matplotlib** to plot functions and visualize results.  
✔ **Fully Tested** → Comes with a test suite to ensure accuracy.  

---

## **Installation**

### **Requirements**
- **Python 3.10** is required.

### **Setup**

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/IslamEssam01/Functions-Solver.git
   cd Functions-Solver
   ```

2. **Set Up a Virtual Environment (Recommended):**
   ```bash
   python -m venv venv  
   source venv/bin/activate  # On Windows, use venv\Scripts\activate  
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## **Usage**

Run the application by executing:
```bash
python main.py
```
Then, input the mathematical expression you want to solve.

---

## **Examples**
<div align="center"> 
   <table> 
      <tr> 
         <td align="center"> <img src="https://github.com/user-attachments/assets/4fcd1503-2502-402a-a191-515e8d23586e" alt="Example 1" width="400"/> </td> 
         <td align="center"> <img src="https://github.com/user-attachments/assets/f2869624-1617-4ea8-85dc-01dda0201645" alt="Example 2" width="400"/> </td> 
      </tr> 
      <tr>
         <td align="center"> <img src="https://github.com/user-attachments/assets/6c427e3e-ef14-427d-be99-63ee3c5638b1" alt="Example 3" width="400"/></td>  
         <td align="center"> <img src="https://github.com/user-attachments/assets/fe32b46a-ddb5-46d4-b66f-4bf9c72c7910" alt="Example 4" width="400"/>  </td>        </tr> 
      <tr>
         <td align="center"> <img src="https://github.com/user-attachments/assets/b1151427-0b21-4eaf-9546-3071cc6fe366" alt="Example 5" width="400"/></td>  
         <td align="center"> <img src="https://github.com/user-attachments/assets/971fb5c6-543b-4f5e-a6a7-bdd3c4715160" alt="Example 6" width="400"/>  </td>        </tr> 
   </table> 
</div>

---

## **How It Works: Pratt Parsing**

This project uses a **Pratt parser** to efficiently parse mathematical expressions.

### **What is Pratt Parsing?**
Pratt parsing is a **top-down operator precedence** parsing technique that dynamically determines how operators bind based on their precedence. It's commonly used for parsing mathematical expressions and programming languages.

### **Why Use Pratt Parsing?**
✔ **Handles complex expressions** with different operator precedences.  
✔ **Efficient and extensible** for supporting new operators and functions.  
✔ **Recursive structure** makes it easy to implement.  

### **How the Parser Works in This Project**
1. **Lexer:** Converts the input expression into tokens (`2*x^2 + 3*x - 5`).  
2. **Parser:** Uses **Pratt parsing** to build an abstract syntax tree (AST).  
3. **Evaluator:** Recursively evaluates the AST to compute the result.  

This design makes the **Functions-Solver** both **fast and scalable** for different types of mathematical expressions.

---

## **Running Tests**

To run the test suite and verify that everything works correctly, use:
```bash
pytest
```
This will execute all tests to ensure the parser and evaluator function as expected.

---

## **Contributing**

Contributions are welcome! To contribute:
1. **Fork** the repository.
2. **Create a new branch:** `git checkout -b feature-branch`
3. **Commit your changes:** `git commit -m "Add new feature"`
4. **Push to your branch:** `git push origin feature-branch`
5. **Open a Pull Request.**

---

## **License**

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

