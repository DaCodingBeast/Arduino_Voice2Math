# MathLibary.py (improved)
from sympy import Function
from math import pi
import re
from sympy import symbols, diff, sin, cos, tan, cot, sec, csc, exp, ln, log, sqrt, asin, acos, atan, sinh, cosh, tanh, zoo
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

class MathProcessor:
    def __init__(self):
        self.x = symbols('x')
        self.local_dict = {
            'sin': sin, 'sign': sin, 'cos': cos, 'tan': tan, 'cot': cot, 'sec': sec, 'csc': csc,
            'exp': exp, 'ln': ln, 'log': log, 'sqrt': sqrt,
            'arcsin': asin, 'arccos': acos, 'arctan': atan, 'cosine': cos, 'tangent': tan,
            'sinh': sinh, 'cosh': cosh, 'tanh': tanh, 'inverse sign': sinh, 'inverse tan': tanh,  'inverse cosine': cosh,  'sine': sin, 'cose' : cos, 'square root': sqrt,
            'x': self.x, 'e': exp(1), 'pi': pi,
        }
        self.transformations = standard_transformations + (implicit_multiplication_application,)
        self.number_words = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
            'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
            'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
            'eighteen': '18', 'nineteen': '19', 'twenty': '20',
            'thirty': '30', 'forty': '40', 'fifty': '50', 'sixty': '60',
            'seventy': '70', 'eighty': '80', 'ninety': '90', 'pie': str(pi), 'pi': str(pi),
        }
        self.magnitude_words = {
            'hundred': 100,
            'thousand': 1_000,
            'million': 1_000_000,
            'billion': 1_000_000_000,
            'trillion': 1_000_000_000_000
        }

    def replace_large_number_phrases(self, text):
        def convert_match(m):
            num_word = m.group(1)
            mag_word = m.group(2)
            if num_word in self.number_words and mag_word in self.magnitude_words:
                num = int(self.number_words[num_word])
                mag = self.magnitude_words[mag_word]
                return str(num * mag)
            return m.group(0)  # fallback

        text = re.sub(
            r'\b(' + '|'.join(self.number_words.keys()) + r')\s+(' + '|'.join(self.magnitude_words.keys()) + r')\b',
            convert_match, text)
        return text

    def replace_number_words(self, text):
        text = self.replace_large_number_phrases(text)
        for word, digit in self.number_words.items():
            pattern = r'\b' + word + r'\b'
            text = re.sub(pattern, digit, text)
        return text

    def replace_power_words(self, text):
        text = re.sub(r'\b([a-zA-Z0-9_]+)\s+squared\b', r'(\1)**2', text)
        text = re.sub(r'\b([a-zA-Z0-9_]+)\s+cubed\b', r'(\1)**3', text)
        text = re.sub(r'\b([a-zA-Z0-9_]+)\s+raised to the (\d+)(?:st|nd|rd|th)? power\b', r'(\1)**\2', text)
        text = re.sub(r'to the (\d+)(?:st|nd|rd|th)? power', r'**\1', text)
        text = re.sub(r'to the power of (\d+)', r'**\1', text)
        return text

    def preprocess(self, text):
        text = text.lower()
        text = self.replace_number_words(text)
        text = self.replace_power_words(text)

        text = re.sub(r'\bcosin\b', 'cos', text)
        text = re.sub(r'\bsing\b', 'sin', text)
        text = re.sub(r'\bover\b', '/', text)

        text = re.sub(r'\btimes\b', '*', text)
        text = re.sub(r'\bplus\b', '+', text)
        text = re.sub(r'\bminus\b', '-', text)
        text = re.sub(r'\bdivided by\b', '/', text)

        text = re.sub(r'\bthe value of\b', '', text)
        text = re.sub(r'\bthe function\b', '', text)
        text = text.strip('?.! ')
        return text

    def get_derivative(self, expr_str, var_str='x'):
        try:
            expr = parse_expr(expr_str, local_dict=self.local_dict, transformations=self.transformations)
            
            # Detect unknown functions
            for f in expr.atoms(Function):
                if f.func.__name__ not in self.local_dict:
                    return None
            
            var = symbols(var_str)
            deriv = diff(expr, var)
            return deriv
        except Exception:
            return None

    def evaluate_expression(self, expr_str):
        try:
            expr_str = re.sub(r'(?<=[0-9)])\s+(?=[0-9(])', '*', expr_str)  # implicit multiplication
            expr_str = expr_str.replace('^', '**')  # Allow ^ for power
            expr = parse_expr(expr_str, local_dict=self.local_dict, transformations=self.transformations)
            val = expr.evalf()

            # Handle sympy zoo (complex infinity) as float('inf')
            if val == zoo:
                return float('inf')
            return val
        except Exception as e:
            return None

    def process_question(self, question):
        question = self.preprocess(question)

        # Derivative queries
        if 'derivative' in question or 'differentiate' in question:
            m = re.search(r'(?:derivative of|differentiate|find the derivative of)\s+(.+)', question)
            if m:
                expr_str = m.group(1).strip()
                deriv = self.get_derivative(expr_str)
                if deriv is None:
                    return None, None
                return str(deriv), deriv

        # Evaluation queries
        m = re.search(r'(?:what is|calculate|evaluate|simplify|compute|find|value of)\s+(.+)', question)
        if m:
            expr_str = m.group(1).strip()
            val = self.evaluate_expression(expr_str)
            if val is None:
                return None, None
            return str(val), val

        # Raw expression fallback
        val = self.evaluate_expression(question)
        if val is not None:
            return str(val), val

        return None, None

    
    def is_definitely_off(self, question, answer):
        if answer is None:
            return True

        try:
            expected_val = self.evaluate_expression(self.preprocess(question))
            answer_val = float(answer)
            if expected_val is None:
                return True
            return abs(expected_val - answer_val) > 1e-4
        except Exception:
            pass  # fallback to symbolic check

        # Derivative check
        processed = self.preprocess(question)
        if 'derivative' in processed or 'differentiate' in processed or 'find the derivative' in processed:
            m = re.search(r'(?:derivative of|differentiate|find the derivative of)\s+(.+)', processed)
            if m:
                expr_str = m.group(1).strip()
                correct_deriv = self.get_derivative(expr_str)
                if correct_deriv is None:
                    return False
                try:
                    ans_expr = parse_expr(str(answer), local_dict=self.local_dict, transformations=self.transformations)
                    corr_expr = parse_expr(str(correct_deriv), local_dict=self.local_dict, transformations=self.transformations)
                    # Use equals instead of subtract-and-simplify
                    return not ans_expr.equals(corr_expr)
                except Exception:
                    return True
            return False

        # Fallback
        return False

        # Numerical evaluation
        try:
            correct_val = float(answer)
            expected_val = float(self.evaluate_expression(processed))
            return abs(correct_val - expected_val) > 1e-4
        except:
            return False


# test_MathLibary.py (improved tests)

import unittest

class TestMathProcessor(unittest.TestCase):
    def setUp(self):
        from MathLibary import MathProcessor
        self.mp = MathProcessor()

    def test_derivative_basic(self):
        question = "What is the derivative of x squared plus three?"
        answer = "2*x + 0"  # 0 from derivative of constant 3
        result, deriv_expr = self.mp.process_question(question)
        self.assertIsNotNone(result)
        # Check simplified equality by parsing
        from sympy import simplify, sympify
        self.assertTrue(simplify(sympify(result) - sympify(answer)) == 0)

    def test_derivative_invalid(self):
        question = "Find the derivative of unknownFunc(x)"
        result, deriv_expr = self.mp.process_question(question)
        self.assertIsNone(result)
        self.assertIsNone(deriv_expr)

    def test_evaluation(self):
        question = "What is 2 plus 2?"
        result, val = self.mp.process_question(question)
        self.assertEqual(float(result), 4.0)

    def test_large_number_word_replacement(self):
        text = "three hundred"
        replaced = self.mp.replace_large_number_phrases(text)
        self.assertEqual(replaced, "300")

    def test_is_definitely_off_numeric(self):
        q = "What is 2 plus 2?"
        self.assertFalse(self.mp.is_definitely_off(q, "4"))

    def test_is_definitely_off_wrong_numeric(self):
        q = "What is 2 plus 2?"
        self.assertTrue(self.mp.is_definitely_off(q, "5"))

    def test_is_definitely_off_derivative(self):
        q = "What is the derivative of x squared?"
        correct_deriv = "2*x"
        wrong_deriv = "3*x"
        self.assertFalse(self.mp.is_definitely_off(q, correct_deriv))
        self.assertTrue(self.mp.is_definitely_off(q, wrong_deriv))

if __name__ == '__main__':
    unittest.main()
