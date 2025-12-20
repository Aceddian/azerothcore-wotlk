import re
import os
from datetime import datetime

def extract_table_name(query):
    query = query.strip().upper()
    patterns = [
        r'FROM\s+`?(\w+)`?',
        r'UPDATE\s+`?(\w+)`?',
        r'INSERT\s+INTO\s+`?(\w+)`?',
        r'DELETE\s+FROM\s+`?(\w+)`?',
        r'INTO\s+`?(\w+)`?'
    ]
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            return match.group(1)
    return None

def extract_query_type(query):
    query = query.strip().upper()
    if query.startswith('SELECT'):
        return 'SELECT'
    elif query.startswith('INSERT'):
        return 'INSERT'
    elif query.startswith('UPDATE'):
        return 'UPDATE'
    elif query.startswith('DELETE'):
        return 'DELETE'
    return 'OTHER'

def compact_select_queries(queries):
    if len(queries) <= 1:
        return queries
    
    base_query = queries[0].strip()
    if not re.search(r'WHERE', base_query, re.IGNORECASE):
        return queries
    
    conditions = []
    for query in queries:
        where_match = re.search(r'WHERE\s+(.+)', query.strip(), re.IGNORECASE | re.DOTALL)
        if where_match:
            condition = where_match.group(1).strip()
            if not condition.endswith(';'):
                condition = condition.rstrip(';')
            conditions.append(f"({condition})")
    
    if conditions:
        base_without_where = re.sub(r'WHERE\s+.+', '', base_query, flags=re.IGNORECASE | re.DOTALL).strip()
        if base_without_where.endswith(';'):
            base_without_where = base_without_where.rstrip(';')
        
        combined_condition = ' OR '.join(conditions)
        compacted = f"{base_without_where} WHERE {combined_condition};"
        return [compacted]
    
    return queries

def compact_delete_queries(queries):
    if len(queries) <= 1:
        return queries
    
    base_query = queries[0].strip()
    table_match = re.search(r'DELETE\s+FROM\s+`?(\w+)`?', base_query, re.IGNORECASE)
    if not table_match:
        return queries
    
    table_name = table_match.group(1)
    
    id_values = []
    all_have_simple_id_condition = True
    id_column = None
    
    for query in queries:
        query = query.strip()
        if query.endswith(';'):
            query = query.rstrip(';')
        
        # Look for patterns like WHERE (`guid`=15) or WHERE `id` = 15 or WHERE guid=15
        id_match = re.search(r'WHERE\s+(?:\()?`?(guid|id)`?\s*=\s*([\'"]?\d+[\'"]?)(?:\))?', query, re.IGNORECASE)
        if id_match:
            if id_column is None:
                id_column = id_match.group(1).lower()
            elif id_column != id_match.group(1).lower():
                all_have_simple_id_condition = False
                break
            
            id_val = id_match.group(2).strip('\'"')
            id_values.append(id_val)
        else:
            all_have_simple_id_condition = False
            break
    
    if all_have_simple_id_condition and id_values and id_column:
        if '`' in base_query:
            compacted = f"DELETE FROM `{table_name}` WHERE `{id_column}` IN ({','.join(id_values)});"
        else:
            compacted = f"DELETE FROM {table_name} WHERE {id_column} IN ({','.join(id_values)});"
        return [compacted]
    
    conditions = []
    for query in queries:
        where_match = re.search(r'WHERE\s+(.+)', query.strip(), re.IGNORECASE | re.DOTALL)
        if where_match:
            condition = where_match.group(1).strip()
            if condition.endswith(';'):
                condition = condition.rstrip(';')
            conditions.append(f"({condition})")
    
    if conditions:
        base_without_where = re.sub(r'WHERE\s+.+', '', base_query, flags=re.IGNORECASE | re.DOTALL).strip()
        if base_without_where.endswith(';'):
            base_without_where = base_without_where.rstrip(';')
        
        combined_condition = ' OR '.join(conditions)
        compacted = f"{base_without_where} WHERE {combined_condition};"
        return [compacted]
    
    return queries

def compact_insert_queries(queries):
    if len(queries) <= 1:
        return queries
    
    base_query = queries[0].strip()
    insert_match = re.search(r'(INSERT\s+INTO\s+`?\w+`?(?:\s*\([^)]+\))?\s+VALUES)', base_query, re.IGNORECASE)
    if not insert_match:
        return queries
    
    insert_part = insert_match.group(1)
    
    all_values = []
    for query in queries:
        query = query.strip()
        if query.endswith(';'):
            query = query.rstrip(';')
        
        values_match = re.search(r'VALUES\s*(.+)', query, re.IGNORECASE | re.DOTALL)
        if values_match:
            values_text = values_match.group(1).strip()
            
            paren_count = 0
            current_value = ""
            in_string = False
            string_char = None
            
            for char in values_text:
                if char in ["'", '"'] and not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char and in_string:
                    in_string = False
                    string_char = None
                
                current_value += char
                
                if not in_string:
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                        if paren_count == 0:
                            all_values.append(current_value.strip())
                            current_value = ""
                            while values_text and values_text[0] in ' ,\t\n':
                                values_text = values_text[1:]
    
    if all_values:
        compacted = f"{insert_part}\n{',\n'.join(all_values)};"
        return [compacted]
    
    return queries

def compact_queries_by_table(queries_by_table):
    compacted = {}
    
    for table, queries in queries_by_table.items():
        queries_by_type = {}
        for query in queries:
            query_type = extract_query_type(query)
            if query_type not in queries_by_type:
                queries_by_type[query_type] = []
            queries_by_type[query_type].append(query)
        
        compacted_queries = []
        for query_type, type_queries in queries_by_type.items():
            if query_type == 'SELECT':
                compacted_queries.extend(compact_select_queries(type_queries))
            elif query_type == 'INSERT':
                compacted_queries.extend(compact_insert_queries(type_queries))
            elif query_type == 'DELETE':
                compacted_queries.extend(compact_delete_queries(type_queries))
            else:
                compacted_queries.extend(type_queries)
        
        compacted[table] = compacted_queries
    
    return compacted

def parse_sql_file(content):
    queries = [q.strip() for q in content.split(';') if q.strip()]
    
    queries_by_table = {}
    other_queries = []
    
    for query in queries:
        if not query.endswith(';'):
            query += ';'
        
        table_name = extract_table_name(query)
        if table_name:
            if table_name not in queries_by_table:
                queries_by_table[table_name] = []
            queries_by_table[table_name].append(query)
        else:
            other_queries.append(query)
    
    return queries_by_table, other_queries

def main():
    filename = input("Enter the SQL file name (must be in the same directory): ").strip()
    
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found in current directory.")
        return
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    queries_by_table, other_queries = parse_sql_file(content)
    
    print(f"\nFound {len(queries_by_table)} tables with queries:")
    for table, queries in queries_by_table.items():
        print(f"  - {table}: {len(queries)} queries")
    
    if other_queries:
        print(f"  - Other queries: {len(other_queries)}")
    
    compacted_queries = compact_queries_by_table(queries_by_table)
    
    print("\nCompacted queries:\n")
    
    total_original = sum(len(queries) for queries in queries_by_table.values())
    total_compacted = sum(len(queries) for queries in compacted_queries.values())
    
    for table, queries in compacted_queries.items():
        for query in queries:
            print(query)
        print()
    
    print(f"Optimization result: {total_original} -> {total_compacted} queries")
    
    save_option = input("Save compacted queries to new file? (y/n): ").strip().lower()
    if save_option == 'y':
        base_name = os.path.splitext(filename)[0]
        timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        output_filename = f"compacted_{base_name}_{timestamp}.sql"
        try:
            with open(output_filename, 'w', encoding='utf-8') as file:
                for table, queries in compacted_queries.items():
                    for query in queries:
                        file.write(query + "\n")
                    file.write("\n")
            
            print(f"Compacted queries saved to '{output_filename}'")
        except Exception as e:
            print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()
