
# Joern server endpoint and credentials
server_endpoint = "localhost:8080"
basic_auth_credentials = ("username", "password")
client = CPGQLSClient(server_endpoint, auth_credentials=basic_auth_credentials)
codebase_path = r"H:\\ros"  # Path to your codebase

def import_codebase():
    """Import the codebase into Joern."""
    try:
        query = import_code_query(codebase_path, "my-c-pl,roect")
        result = client.execute(query)
        print("Codebase imported successfully.")
        return result
    except Exception as e:
        print(f"An error occurred while importing the codebase: {e}")

# Example of a multi-line query with corrected file path
multi_line_query = """
def getChildHierarchy(funcName: String): Map[String, List[String]] = {
  // Initialize with the starting function
  val stack = scala.collection.mutable.Stack(funcName)
  val hierarchy = scala.collection.mutable.Map[String, List[String]]().withDefaultValue(List())

  // Iterate over the stack
  while (stack.nonEmpty) {
    val currentFunc = stack.pop()
    val callees = cpg.file.nameExact("tools\\\\rosmake\\\\src\\\\rosmake\\\\engine.py").method.name(currentFunc).call("[^<].*").name.l.distinct

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
val hierarchy = getChildHierarchy("main")
def getSkipPatterns: Set[String] = Set(
  "<operator>.", // Skipping operators
  "<operator>.fieldAccess", "<operator>.slice", "<operator>.tupleLiteral", // Special operators
  "int<meta>", "str<meta>", "list<meta>", "range<meta>", // Meta-functions
  "__init__", "__iter__", "__next__", "__builtin.open.<returnValue>.", "threading.py:<module>.Lock.<returnValue>.", // Special attributes/methods
  "append", "split", "sort", "keys", "values", "items", "enumerate", "filter" // Data operations
)
val skipPatterns = getSkipPatterns
def buildNestedHierarchy(
  hierarchy: Map[String, List[String]], 
  func: String, 
  skipPatterns: Set[String], 
  maxDepth: Int = 10, 
  currentDepth: Int = 0, 
  processing: Set[String] = Set()
): Map[String, Any] = {
  if (currentDepth >= maxDepth || func.isEmpty) 
    Map(func -> "max depth reached")
  else if (processing.contains(func)) 
    Map(func -> "(recursive)")
  else if (skipPatterns.exists(func.contains)) 
    Map()
  else {
    val newProcessing = processing + func
    val children = hierarchy.getOrElse(func, List()).flatMap { callee =>
      buildNestedHierarchy(hierarchy, callee, skipPatterns, maxDepth, currentDepth + 1, newProcessing).toList
    }.toMap
    Map(func -> children)
  }
}
val nestedHierarchy: Map[String, Any] = buildNestedHierarchy(hierarchy, "main", skipPatterns)
"""

# Function to strip ANSI color codes from the output
def strip_ansi_codes(text):
    ansi_escape = re.compile(r'\x1b\[.*?m')
    return ansi_escape.sub('', text)

import_codebase()
# Execute the multi-line query
result = client.execute(multi_line_query)

# Get the raw output from stdout
raw_output = result['stdout']

# Clean the ANSI codes from the output
cleaned_output = strip_ansi_codes(raw_output)

# Extract the relevant part of the output after 'def buildHierarchy'
if 'def buildNestedHierarchy' in cleaned_output:
    relevant_output = cleaned_output.split('def buildNestedHierarchy')[1]
    # Extract the part of the output starting with 'Map('
    if 'Map[String, Any] = ' in relevant_output:
        scala_str = relevant_output.split('Map[String, Any] = ')[1]
        scala_str = scala_str.replace('->', ' : ').replace('HashMap(', ' { ')   .replace('Map(', '{').replace('Map()', '{}').replace(')', ' } ')
        dic = json.loads(scala_str)
        print(dic)
#{'main': {'get_profile_string': {'float': {}}, 'OptionParser': {}, 'generate_summary_output': {'join': {}, 'open': {}, 'print_all': {'write': {}, 'flush': {}, 'pad_str_to_width': {'len': {}}, 'terminal_width': {'pack': {}, 'ioctl': {}, 'unpack': {}, 'int': {}}}, 'write': {}, 'len': {}, 'get_profile_string': {'float': {}}, '': 'max depth reached'}, 'add_option': {}, 'float': {}, 'remove_nobuild': {}, 'extend': {}, 'expand_to_packages': {}, 'DependencyTracker': {}, 'add_nobuild': {}, 'can_build': {}, 'get_ros_home': {}, 'get_depends_on': {}, 'samefile': {}, 'join': {}, 'isdir': {}, 'print_verbose': {'print_all': {'write': {}, 'flush': {}, 'pad_str_to_width': {'len': {}}, 'terminal_width': {'pack': {}, 'ioctl': {}, 'unpack': {}, 'int': {}}}}, 'set': {}, 'parse_args': {}, 'get_depends': {}, 'BuildQueue': {}, 'basename': {}, 'get_path': {}, 'strftime': {}, 'parallel_build_pkgs': {'': 'max depth reached', 'join': {}, 'str': {}, 'print_all': {'write': {}, 'flush': {}, 'pad_str_to_width': {'len': {}}, 'terminal_width': {'pack': {}, 'ioctl': {}, 'unpack': {}, 'int': {}}}, 'range': {}, 'CompileThread': {}, 'start': {}, 'stop': {}, 'succeeded': {}}, 'print_all': {'write': {}, 'flush': {}, 'pad_str_to_width': {'len': {}}, 'terminal_width': {'pack': {}, 'ioctl': {}, 'unpack': {}, 'int': {}}}, 'num_cpus': {}, 'exists': {}, 'exit': {}, 'abspath': {}, 'build_or_recurse': {'get_path': {}, 'print_all': {'write': {}, 'flush': {}, 'pad_str_to_width': {'len': {}}, 'terminal_width': {'pack': {}, 'ioctl': {}, 'unpack': {}, 'int': {}}}, 'exit': {}, 'build_or_recurse': '(recursive } ', 'get_deps_1': {}}, 'get': {}, 'time': {}, 'list': {}, 'len': {}, 'makedirs_with_parent_perms': {'dirname': {}, 'exists': {}, 'abspath': {}, 'chown': {}, 'stat': {}, 'mkdir': {}, 'makedirs_with_parent_perms': '(recursive } ', 'chmod': {}}}}



