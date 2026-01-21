import os
import re
from openai import OpenAI
from config import Config

class AIFixer:
    """Module responsible for interacting with LLM to fix code."""

    def __init__(self):
        self.client = OpenAI(
            api_key=Config.LLM_API_KEY,
            base_url=Config.LLM_BASE_URL
        )

    def get_file_context(self, file_path, line_num, context_lines=20):
        """Read file and extract context around the error."""
        if not os.path.exists(file_path):
            return None, None, None

        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        start_line = max(0, line_num - context_lines)
        end_line = min(len(lines), line_num + context_lines)
        code_context = "".join(lines[start_line:end_line])
        
        return lines, start_line, end_line, code_context

    def generate_fix(self, error_msg, file_path, line_num, code_context, language="java"):
        """Call LLM to generate fixed code."""
        prompt = f"""
        I am upgrading dependencies in a {language} project and encountered an error.
        
        Error Message: {error_msg}
        File: {file_path}
        Line: {line_num}
        
        Code Context:
        ```{language}
        {code_context}
        ```
        
        Please provide the corrected {language} code for the provided context. 
        Only return the corrected code block (no explanations). 
        Ensure the indentation matches.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": f"You are an expert {language} developer fixing errors caused by dependency upgrades."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            
            content = response.choices[0].message.content
            
            # Extract code block
            # Try specific language first, then generic
            code_match = re.search(f"```{language}\n(.*?)```", content, re.DOTALL)
            if not code_match:
                 code_match = re.search(r"```\n(.*?)```", content, re.DOTALL)

            if code_match:
                return code_match.group(1)
            else:
                # Fallback: remove markdown code fences if present
                clean_content = content.strip().replace(f"```{language}", "").replace("```", "")
                return clean_content
                
        except Exception as e:
            print(f"LLM interaction failed: {e}")
            return None

    def apply_fix(self, file_path, lines, start_line, end_line, fixed_code):
        """Apply the fix to the file."""
        try:
            # Ensure fixed_code ends with newline if needed
            if not fixed_code.endswith("\n"):
                fixed_code += "\n"
                
            # Naive replacement - assuming LLM returns the exact chunk to replace
            # In reality, might need diff matching, but this is a stub/prototype
            lines[start_line:end_line] = [fixed_code]
            
            with open(file_path, 'w') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"Error writing file {file_path}: {e}")
            return False

    def fix_error(self, error_info, project_type="maven"):
        """Main method to handle the fix process for a single error."""
        file_path = error_info['file']
        line_num = error_info['line']
        error_msg = error_info['msg']
        
        # Map project type to language
        lang_map = {
            "maven": "java",
            "pip": "python",
            "npm": "javascript" # or typescript, could check file extension
        }
        language = lang_map.get(project_type, "java")
        
        # If file extension contradicts, prefer file extension
        if file_path.endswith(".py"):
            language = "python"
        elif file_path.endswith(".js"):
            language = "javascript"
        elif file_path.endswith(".ts"):
            language = "typescript"
        
        print(f"  Requesting AI fix for {os.path.basename(file_path)}:{line_num} ({language})...")
        
        lines, start, end, context = self.get_file_context(file_path, line_num)
        if not context:
            print("  Could not read file context.")
            return False
            
        fixed_code = self.generate_fix(error_msg, file_path, line_num, context, language)
        if not fixed_code:
            print("  LLM did not return a valid fix.")
            return False
            
        if self.apply_fix(file_path, lines, start, end, fixed_code):
            print("  Fix applied successfully.")
            return True
        return False

if __name__ == "__main__":
    print("AIFixer module ready.")
