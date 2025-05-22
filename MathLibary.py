import re
from sympy import symbols, diff, sin, cos, tan, cot, sec, csc, exp, ln, log, sqrt, asin, acos, atan, sinh, cosh, tanh
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

class MathProcessor:
    def __init__(self):
        self.x = symbols('x')
        self.local_dict = {
            'sin': sin, 'cos': cos, 'tan': tan, 'cot': cot, 'sec': sec, 'csc': csc,
            'exp': exp, 'ln': ln, 'log': log, 'sqrt': sqrt,
            'arcsin': asin, 'arccos': acos, 'arctan': atan,
            'sinh': sinh, 'cosh': cosh, 'tanh': tanh,
            'x': self.x, 'e': exp(1)
        }
        self.transformations = standard_transformations + (implicit_multiplication_application,)
        self.number_words = {
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
            'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
            'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
            'eighteen': '18', 'nineteen': '19', 'twenty': '20',
            'thirty': '30', 'forty': '40', 'fifty': '50', 'sixty': '60',
            'seventy': '70', 'eighty': '80', 'ninety': '90'
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
        # squared and cubed for digits or variables (letters/digits/underscore)
        text = re.sub(r'\b([a-zA-Z0-9_]+)\s+squared\b', r'(\1)**2', text)
        text = re.sub(r'\b([a-zA-Z0-9_]+)\s+cubed\b', r'(\1)**3', text)
        
        # raised to the nth power (for base digits or variables)
        text = re.sub(r'\b([a-zA-Z0-9_]+)\s+raised to the (\d+)(?:st|nd|rd|th)? power\b', r'(\1)**\2', text)
        
        # to the nth power (general)
        text = re.sub(r'to the (\d+)(?:st|nd|rd|th)? power', r'**\1', text)
        
        # to the power of n
        text = re.sub(r'to the power of (\d+)', r'**\1', text)
        
        return text

    def preprocess(self, text):
        text = text.lower()
        text = self.replace_number_words(text)
        text = self.replace_power_words(text)

        # Correct common math language
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
            var = symbols(var_str)
            deriv = diff(expr, var)
            return deriv
        except Exception as e:
            return f"Failed to compute derivative: {e}"

    def evaluate_expression(self, expr_str):
        try:
            expr_str = re.sub(r'(?<=[0-9)])\s+(?=[0-9(])', '*', expr_str)  # implicit multiplication
            expr_str = expr_str.replace('^', '**')  # Allow ^ for power
            expr = parse_expr(expr_str, local_dict=self.local_dict, transformations=self.transformations)
            return expr.evalf()
        except Exception as e:
            return f"Failed to evaluate expression: {e}"

    def process_question(self, question):
        question = self.preprocess(question)

        # Derivative queries
        if 'derivative' in question or 'differentiate' in question:
            m = re.search(r'(?:derivative of|differentiate|find the derivative of)\s+(.+)', question)
            if m:
                expr_str = m.group(1).strip()
                deriv = self.get_derivative(expr_str)
                if isinstance(deriv, str) and deriv.startswith("Failed"):
                    return None, None
                return str(deriv), deriv

        # Evaluation queries
        m = re.search(r'(?:what is|calculate|evaluate|simplify|compute|find|value of)\s+(.+)', question)
        if m:
            expr_str = m.group(1).strip()
            val = self.evaluate_expression(expr_str)
            if isinstance(val, str) and val.startswith("Failed"):
                return None, None
            return str(val), val

        # Raw expression fallback
        try:
            val = self.evaluate_expression(question)
            if not (isinstance(val, str) and val.startswith("Failed")):
                return str(val), val
        except:
            pass

        return None, None

    def is_definitely_off(self, question, answer):
        if answer is None:
            return True

        if re.search(r'[a-zA-Z]{2,}', answer) and not any(func in answer for func in [
            'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'exp', 'ln', 'log', 'sqrt',
            'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh']):
            return True

        processed = self.preprocess(question)

        if 'derivative' in processed or 'differentiate' in processed or 'find the derivative' in processed:
            m = re.search(r'(?:derivative of|differentiate|find the derivative of)\s+(.+)', processed)
            if m:
                expr_str = m.group(1).strip()
                correct_deriv = self.get_derivative(expr_str)
                if isinstance(correct_deriv, str) and correct_deriv.startswith("Failed"):
                    return False
                try:
                    ans_expr = parse_expr(answer, local_dict=self.local_dict, transformations=self.transformations)
                    corr_expr = parse_expr(str(correct_deriv), local_dict=self.local_dict, transformations=self.transformations)
                    return (ans_expr - corr_expr).simplify() != 0
                except:
                    return True
            return False

        try:
            correct_val = self.evaluate_expression(processed)
            if isinstance(correct_val, str) and correct_val.startswith("Failed"):
                return False
            try:
                user_val = float(answer)
                correct_num = float(correct_val)
                return abs(user_val - correct_num) > 1e-6
            except:
                return False
        except:
            return False

    def process_and_check(self, question):
        answer, _ = self.process_question(question)
        if self.is_definitely_off(question, answer):
            return "Could not Compute"
        return answer if answer is not None else "Could not Compute"
