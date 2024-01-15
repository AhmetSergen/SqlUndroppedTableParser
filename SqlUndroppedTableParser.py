import sys
import re # regular expression

print("\n__________ SQL Undropped Table Parser __________")

if(sys.version_info.major < 3 or (sys.version_info.major >= 3 and sys.version_info.minor < 6)):
    print("Minimum compatible python version is 3.6")
    quit();

fileFound = False
while (fileFound == False):
    file_path = input("File Path: ")

    try:
        file = open(file_path, 'r', encoding="utf-8") # type help(open) for information about method
        query = file.read();
        file = open(file_path, 'r', encoding="utf-8")
        queryLineByLine = file.readlines();
        file.close();
        fileFound = True
    except FileNotFoundError:
        print("File not found. Please specify the file path correctly.")

createdTablesWithCreateTableStatement = re.findall(r"(?<=create\x20table\x20)[\x20]*[^\x20|\(]+(?=\x20|\()", query, re.IGNORECASE);

selectIntoStatements = re.findall(r"select\s+.*\sinto\s+.+", query, re.IGNORECASE); # Find all select into statements entirely

createdTablesWithSelectIntoStatement = [];
for index in range(len(selectIntoStatements)): # Find created table names among select into statements
    createdTablesWithSelectIntoStatement += re.findall(r"(?<=into\s)\s*[^\s|;]*", selectIntoStatements[index], re.IGNORECASE);

createdTables = createdTablesWithCreateTableStatement + createdTablesWithSelectIntoStatement;
for index in range(len(createdTables)): 
    createdTables[index] = createdTables[index].replace(" ", "") #Remove spaces from table names
#print(createdTables)

droppedTables = re.findall(r"(?<=drop\x20table\x20).*$((?![\r\n])|\n|\s)", query, re.IGNORECASE)
for index in range(len(droppedTables)): 
    droppedTables[index] = droppedTables[index].replace(" ", "").replace(";", "") #Remove spaces from table names
#print(droppedTables)

# In case of multi drop table usage (ex: drop table table1, table2), seperate table names according to commas
droppedTablesSeperated = [];
for i in range(len(droppedTables)): droppedTablesSeperated += droppedTables[i].split(",")

# Check if there are any created but not dropped tables in query
undroppedTables = []
for x in range(len(createdTables)):
    currentTable = createdTables[x]
    isCurrentTableDropped = False;
    for y in range(len(droppedTablesSeperated)):
        if (currentTable == droppedTablesSeperated[y]):
            isCurrentTableDropped = True;
            break;
    if (isCurrentTableDropped == False):
        undroppedTables.append(currentTable);

undroppedTablesDictionary = {} # {"tempTableName" : Last_Line_Encountered_Table}
for item in undroppedTables: undroppedTablesDictionary.update({item : None})

# Find last used line numbers for undropped temp tables
for lineNumber in range(len(queryLineByLine)):   
    for item in undroppedTablesDictionary:
        if (re.search(item, queryLineByLine[lineNumber])): undroppedTablesDictionary[item] = lineNumber + 1
        

# Print Results:

print("\nCreated Tables:\n"+','.join(str(x) for x in createdTables))
print("\nDropped Tables:\n"+','.join(str(x) for x in droppedTablesSeperated))
# print("\nUndropped Temp Tables:\n"+','.join(str(x) for x in undroppedTables))
print("\nUndropped Tables ([ Last_Line_Encountered_Table ] TableName ):")
for key, value in undroppedTablesDictionary.items():
    print('[', value, ']', key)