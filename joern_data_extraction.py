import re
import ast
import json
from cpgqls_client import CPGQLSClient, import_code_query
import data_cleaning as dtc
import subprocess
import pickle

# def start_joern_server():
    # try:
        # # Specify the path to the directory containing the Joern executable
        # joern_directory = r"E:\joern\joern-cli"

        # # Command to run Joern server
        # command = "joern.bat --server"

        # # Start the Joern server from the specified directory
        # process = subprocess.Popen(command, shell=True, cwd=joern_directory)

        # print("Joern server started successfully as a background process.")

    # except Exception as e:
        # print(f"An error occurred: {e}")
        
# Joern server endpoint and credentials
server_endpoint = "localhost:8080"
basic_auth_credentials = ("username", "password")
client = CPGQLSClient(server_endpoint, auth_credentials = basic_auth_credentials)
codebase_path = r"H:\\linux-master\\kernel"  # Path to your codebase
#codebase_path = ""

# Function to strip ANSI color codes from the output
def strip_ansi_codes(text):
    ansi_escape = re.compile(r'\x1b\[.*?m')
    return ansi_escape.sub('', text)

def import_codebase():
    """Import the codebase into Joern."""
    # global codebase_path
    # codebase_path = input("Enter the Codebase PATH")
    try:
        query = import_code_query(codebase_path, "wedew)&hi9[+]%^89087pp")
        result = client.execute(query)
        print("Codebase imported successfully.")
        return result
    except Exception as e:
        print(f"An error occurred while importing the codebase: {e}")

def run_query(query):
    """Run a specific Joern query and return the results."""
    try:
        raw_output = client.execute(query)
        result = raw_output['stdout']
        cleaned_output = strip_ansi_codes(result)  # Clean the ANSI codes from the output
        return cleaned_output
    except Exception as e:
        print(f"Error running query: {e}")
        return None
        
# Example of a multi-line query with corrected file path
get_child_hierarchy ='''
def getChildHierarchy(funcName: String): Map[String, List[String]] = {
  // Initialize with the starting function
  val stack = scala.collection.mutable.Stack(funcName)
  val hierarchy = scala.collection.mutable.Map[String, List[String]]().withDefaultValue(List())

  // Iterate over the stack
  while (stack.nonEmpty) {
    val currentFunc = stack.pop()
    val callees = cpg.method.name(currentFunc).call("[^<].*").name.l.distinct

    // Update the hierarchy map
    hierarchy(currentFunc) = callees.toList

    // Push new callees onto the stack for further processing
    callees.foreach { callee =>
      if (!hierarchy.contains(callee)) {
        stack.push(callee)
      }
    }
  }

  hierarchy.toMap
}
val hierarchy = getChildHierarchy("bpf_struct_ops_map_update_elem")
''' 
get_skip_patterns='''
def getSkipPatterns: Set[String] = Set(
  "<operator>.", // Skipping operators
  "<operator>.fieldAccess", "<operator>.slice", "<operator>.tupleLiteral", // Special operators
  "int<meta>", "str<meta>", "list<meta>", "range<meta>", // Meta-functions
  "__init__", "__iter__", "__next__", "__builtin.open.<returnValue>.", "threading.py:<module>.Lock.<returnValue>.", // Special attributes/methods
  "append", "split", "sort", "keys", "values", "items", "enumerate", "filter" // Data operations
)
val skipPatterns = getSkipPatterns
'''
get_hierarchy_dict = '''
def buildHierarchyDict(hierarchy: Map[String, List[String]], func: String, skipPatterns: Set[String], visited: Set[String] = Set(), maxDepth: Int = 1, currentDepth: Int = 0): Map[String, Any] = {
  
  if (currentDepth > maxDepth) 
    return Map(func -> "max depth reached")
  
  if (visited.contains(func)) 
    return Map(func -> "recursive")
  
  if (!skipPatterns.exists(func.contains)) {
    hierarchy.get(func) match {
      case Some(callees) =>
        val newVisited = visited + func
        Map(func -> callees.filterNot(callee => skipPatterns.exists(callee.contains))
                           .map(callee => buildHierarchyDict(hierarchy, callee, skipPatterns, newVisited, maxDepth, currentDepth + 1)))
      case None => Map(func -> List.empty)
    }
  } else {
    Map.empty
  }
}
val hierarchyDict = buildHierarchyDict(hierarchy, "bpf_struct_ops_map_update_elem", skipPatterns)
'''
var_query = '''
val All_Functions_in_Hierarchy = (hierarchy.keys ++ hierarchy.values.flatten.l.distinct).l.distinct
cpg.identifier.name("varr").method.name.l.distinct
val functionsWithMyVar = All_Functions_in_Hierarchy.filter(fn =>cpg.method.name(fn).ast.isIdentifier.name("varr").nonEmpty)
'''
def initialization():
    #start_joern_server()
    with open(r"H:\github\static_code_analysis_tool\path.pkl", 'rb') as f:
        path_in_file = pickle.load(f)
    if codebase_path == path_in_file:
        return dtc.get_data()
    else :
        import_codebase()
        result = run_query(get_child_hierarchy)
        result = run_query(get_skip_patterns)
        result = run_query(get_hierarchy_dict)
        result = dtc.correct_brackets(result)
        result = result.split('val hierarchyDict: Map[String, Any] = ')[1]
        result = json.loads(result)
        dtc.storing_data(codebase_path,result)
        return result

def variable_search(fun , var_name):
    #initialization()
    var_hierarchy = get_child_hierarchy.replace('bpf_struct_ops_map_update_elem',fun)
    result = run_query(var_hierarchy)
    local_var_query = var_query.replace('varr' , var_name)
    result = run_query(local_var_query)
    result = result.split("functionsWithMyVar: List[String] = List")[1].replace('(','[').replace(')',']')
    result = json.loads(result)
    return result
   

# output_functions = variable_search('bpf_struct_ops_map_update_elem' , 'PERF_RECORD_KSYMBOL_TYPE_UNKNOWN')  
# print(output_functions)
# print(type(output_functions))
# a= initialization()
# print(a)


