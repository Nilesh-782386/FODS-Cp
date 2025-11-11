#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>
#include <limits.h>
#include <errno.h>

// Maximum size for arrays and data structures
#define MAX_SIZE 100
#define MAX_STEPS 1000
#define MAX_INPUT_LENGTH 1000
#define MIN_ARRAY_SIZE 1
#define MAX_ARRAY_SIZE 50

// Error codes
#define SUCCESS 0
#define ERROR_INVALID_INPUT -1
#define ERROR_MEMORY_ALLOCATION -2
#define ERROR_FILE_OPERATION -3
#define ERROR_INVALID_SIZE -4

// Structure for storing algorithm steps
typedef struct {
    char action[50];
    int data[MAX_SIZE];
    int size;
    int highlighted[MAX_SIZE];
    int pointers[10];
    char description[200];
    char complexity[50];
} Step;

// Binary Tree Node
typedef struct TreeNode {
    int data;
    struct TreeNode* left;
    struct TreeNode* right;
} TreeNode;

// Linked List Node
typedef struct ListNode {
    int data;
    struct ListNode* next;
} ListNode;

// Stack structure
typedef struct {
    int arr[MAX_SIZE];
    int top;
} Stack;

// Queue structure
typedef struct {
    int arr[MAX_SIZE];
    int front, rear;
} Queue;

// Global variables
Step steps[MAX_STEPS];
int step_count = 0;
TreeNode* root = NULL;
ListNode* head = NULL;
Stack stack = {.top = -1};
Queue queue = {.front = -1, .rear = -1};

// Function prototypes
void add_step(char* action, int* data, int size, int* highlighted, int* pointers, char* desc, char* complexity);
int write_json_output();
int write_config(char* structure_type, char* operation);
void generate_random_array(int* arr, int size, int min, int max);

// Input validation functions
int validate_array_size(int size);
int validate_menu_choice(int choice, int min, int max);
int safe_input_int(const char* prompt, int* value, int min, int max);
int safe_input_array(int* arr, int size);
void clear_input_buffer();
void cleanup_memory();

// Binary Tree operations
TreeNode* create_node(int data);
TreeNode* insert_bst(TreeNode* root, int data);
TreeNode* search_bst(TreeNode* root, int data);
TreeNode* delete_bst(TreeNode* root, int data);
void inorder_traversal(TreeNode* root, int* arr, int* index);
void tree_to_array(TreeNode* root, int* arr, int* index, int level, int max_nodes);

// Linked List operations
void insert_at_beginning(int data);
void insert_at_end(int data);
void insert_sequential(int data);
void search_linked_list(int data);

// Stack operations
void push(int data);
int pop();

// Queue operations
void enqueue(int data);
int dequeue();

// Searching algorithms
void linear_search(int* arr, int size, int target);
void binary_search(int* arr, int size, int target);

// Sorting algorithms
void bubble_sort(int* arr, int size);
void selection_sort(int* arr, int size);
void insertion_sort(int* arr, int size);
void quick_sort_wrapper(int* arr, int size);
void quick_sort(int* arr, int low, int high, int original_size);
int partition(int* arr, int low, int high, int original_size);
void merge_sort_wrapper(int* arr, int size);
void merge_sort(int* arr, int left, int right, int* original_arr, int original_size);
void merge(int* arr, int left, int mid, int right, int* original_arr, int original_size);

// Utility functions
void swap(int* a, int* b);
void copy_array(int* dest, int* src, int size);

// Input validation functions implementation
int validate_array_size(int size) {
    if (size < MIN_ARRAY_SIZE) {
        printf("Error: Array size must be at least %d\n", MIN_ARRAY_SIZE);
        return ERROR_INVALID_SIZE;
    }
    if (size > MAX_ARRAY_SIZE) {
        printf("Error: Array size cannot exceed %d (for better visualization)\n", MAX_ARRAY_SIZE);
        return ERROR_INVALID_SIZE;
    }
    return SUCCESS;
}

int validate_menu_choice(int choice, int min, int max) {
    if (choice < min || choice > max) {
        printf("Error: Please enter a number between %d and %d\n", min, max);
        return ERROR_INVALID_INPUT;
    }
    return SUCCESS;
}

void clear_input_buffer() {
    int c;
    while ((c = getchar()) != '\n' && c != EOF);
}

int safe_input_int(const char* prompt, int* value, int min, int max) {
    char input[MAX_INPUT_LENGTH];
    char* endptr;
    long int temp;
    
    while (1) {
        printf("%s", prompt);
        if (fgets(input, sizeof(input), stdin) == NULL) {
            printf("Error: Input reading failed\n");
            return ERROR_INVALID_INPUT;
        }
        
        // Remove newline character
        input[strcspn(input, "\n")] = 0;
        
        // Convert to integer
        errno = 0;
        temp = strtol(input, &endptr, 10);
        
        // Check for conversion errors
        if (errno != 0 || endptr == input || *endptr != '\0') {
            printf("Error: Please enter a valid integer\n");
            continue;
        }
        
        // Check range
        if (temp < min || temp > max) {
            printf("Error: Please enter a number between %d and %d\n", min, max);
            continue;
        }
        
        // Check for overflow
        if (temp < INT_MIN || temp > INT_MAX) {
            printf("Error: Number too large\n");
            continue;
        }
        
        *value = (int)temp;
        return SUCCESS;
    }
}

int safe_input_array(int* arr, int size) {
    printf("Enter %d elements (one per line):\n", size);
    for (int i = 0; i < size; i++) {
        char input[MAX_INPUT_LENGTH];
        char* endptr;
        long int temp;
        
        while (1) {
            printf("Element %d: ", i + 1);
            if (fgets(input, sizeof(input), stdin) == NULL) {
                printf("Error: Input reading failed\n");
                return ERROR_INVALID_INPUT;
            }
            
            // Remove newline character
            input[strcspn(input, "\n")] = 0;
            
            // Convert to integer
            errno = 0;
            temp = strtol(input, &endptr, 10);
            
            // Check for conversion errors
            if (errno != 0 || endptr == input || *endptr != '\0') {
                printf("Error: Please enter a valid integer\n");
                continue;
            }
            
            // Check for overflow
            if (temp < INT_MIN || temp > INT_MAX) {
                printf("Error: Number too large\n");
                continue;
            }
            
            arr[i] = (int)temp;
            break;
        }
    }
    return SUCCESS;
}

void cleanup_memory() {
    // Free BST memory
    while (root != NULL) {
        root = delete_bst(root, root->data);
    }
    
    // Free linked list memory
    while (head != NULL) {
        ListNode* temp = head;
        head = head->next;
        free(temp);
    }
    
    // Reset stack and queue
    stack.top = -1;
    queue.front = -1;
    queue.rear = -1;
    step_count = 0;
}

// Add step to visualization with enhanced information
void add_step(char* action, int* data, int size, int* highlighted, int* pointers, char* desc, char* complexity) {
    if (step_count >= MAX_STEPS) return;
    
    strcpy(steps[step_count].action, action);
    steps[step_count].size = size;
    
    for (int i = 0; i < size && i < MAX_SIZE; i++) {
        steps[step_count].data[i] = data[i];
        steps[step_count].highlighted[i] = highlighted ? highlighted[i] : 0;
    }
    
    for (int i = 0; i < 10; i++) {
        steps[step_count].pointers[i] = pointers ? pointers[i] : -1;
    }
    
    // Ensure description and complexity are properly copied
    strncpy(steps[step_count].description, desc, 199);
    steps[step_count].description[199] = '\0';
    
    strncpy(steps[step_count].complexity, complexity, 49);
    steps[step_count].complexity[49] = '\0';
    
    step_count++;
}

// Generate random array
void generate_random_array(int* arr, int size, int min, int max) {
    for (int i = 0; i < size; i++) {
        arr[i] = rand() % (max - min + 1) + min;
    }
}

// Utility functions
void swap(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

void copy_array(int* dest, int* src, int size) {
    for (int i = 0; i < size; i++) {
        dest[i] = src[i];
    }
}

// Binary Tree functions
TreeNode* create_node(int data) {
    TreeNode* node = (TreeNode*)malloc(sizeof(TreeNode));
    node->data = data;
    node->left = NULL;
    node->right = NULL;
    return node;
}

TreeNode* insert_bst(TreeNode* root, int data) {
    if (root == NULL) {
        root = create_node(data);
        
        int tree_arr[MAX_SIZE] = {0};
        int index = 0;
        tree_to_array(root, tree_arr, &index, 0, MAX_SIZE);
        int highlighted[MAX_SIZE] = {0};
        highlighted[0] = 1;
        
        add_step("INSERT_BST", tree_arr, index, highlighted, NULL, 
                 "Inserted root node", "O(1)");
        return root;
    }
    
    if (data < root->data) {
        root->left = insert_bst(root->left, data);
    } else if (data > root->data) {
        root->right = insert_bst(root->right, data);
    }
    
    int tree_arr[MAX_SIZE] = {0};
    int index = 0;
    tree_to_array(root, tree_arr, &index, 0, MAX_SIZE);
    int highlighted[MAX_SIZE] = {0};
    
    for (int i = 0; i < index; i++) {
        if (tree_arr[i] == data) {
            highlighted[i] = 1;
            break;
        }
    }
    
    add_step("INSERT_BST", tree_arr, index, highlighted, NULL, 
             "Node inserted in BST", "O(log n)");
    
    return root;
}

void tree_to_array(TreeNode* root, int* arr, int* index, int level, int max_nodes) {
    if (root == NULL || *index >= max_nodes) return;
    
    arr[*index] = root->data;
    (*index)++;
    
    if (root->left) tree_to_array(root->left, arr, index, level + 1, max_nodes);
    if (root->right) tree_to_array(root->right, arr, index, level + 1, max_nodes);
}

TreeNode* search_bst(TreeNode* root, int data) {
    int tree_arr[MAX_SIZE] = {0};
    int index = 0;
    int highlighted[MAX_SIZE] = {0};
    
    TreeNode* current = root;
    
    while (current != NULL) {
        index = 0;
        memset(tree_arr, 0, sizeof(tree_arr));
        memset(highlighted, 0, sizeof(highlighted));
        tree_to_array(root, tree_arr, &index, 0, MAX_SIZE);
        
        for (int i = 0; i < index; i++) {
            if (tree_arr[i] == current->data) {
                highlighted[i] = 1;
                break;
            }
        }
        
        char desc[200];
        sprintf(desc, "Searching for %d, checking node %d", data, current->data);
        add_step("SEARCH_BST", tree_arr, index, highlighted, NULL, desc, "O(log n)");
        
        if (data == current->data) {
            for (int i = 0; i < index; i++) {
                if (tree_arr[i] == data) {
                    highlighted[i] = 2;
                    break;
                }
            }
            add_step("SEARCH_BST_FOUND", tree_arr, index, highlighted, NULL, 
                     "Target found!", "O(log n)");
            return current;
        } else if (data < current->data) {
            current = current->left;
        } else {
            current = current->right;
        }
    }
    
    add_step("SEARCH_BST_NOT_FOUND", tree_arr, index, highlighted, NULL, 
             "Target not found", "O(log n)");
    return NULL;
}

TreeNode* delete_bst(TreeNode* root, int data) {
    if (root == NULL) {
        int tree_arr[MAX_SIZE] = {0};
        int highlighted[MAX_SIZE] = {0};
        add_step("DELETE_BST_NOT_FOUND", tree_arr, 0, highlighted, NULL, 
                 "Element not found in BST", "O(log n)");
        return root;
    }
    
    int tree_arr[MAX_SIZE] = {0};
    int index = 0;
    tree_to_array(root, tree_arr, &index, 0, MAX_SIZE);
    int highlighted[MAX_SIZE] = {0};
    
    for (int i = 0; i < index; i++) {
        if (tree_arr[i] == root->data) {
            highlighted[i] = 1;
            break;
        }
    }
    
    char desc[200];
    sprintf(desc, "Searching for %d to delete, checking node %d", data, root->data);
    add_step("DELETE_BST_SEARCH", tree_arr, index, highlighted, NULL, desc, "O(log n)");
    
    if (data < root->data) {
        root->left = delete_bst(root->left, data);
    } else if (data > root->data) {
        root->right = delete_bst(root->right, data);
    } else {
        memset(highlighted, 0, sizeof(highlighted));
        for (int i = 0; i < index; i++) {
            if (tree_arr[i] == data) {
                highlighted[i] = 2;
                break;
            }
        }
        add_step("DELETE_BST_FOUND", tree_arr, index, highlighted, NULL, 
                 "Node found - proceeding with deletion", "O(log n)");
        
        if (root->left == NULL) {
            TreeNode* temp = root->right;
            free(root);
            return temp;
        } else if (root->right == NULL) {
            TreeNode* temp = root->left;
            free(root);
            return temp;
        }
        
        TreeNode* temp = root->right;
        while (temp->left != NULL) {
            temp = temp->left;
        }
        
        root->data = temp->data;
        root->right = delete_bst(root->right, temp->data);
    }
    
    memset(tree_arr, 0, sizeof(tree_arr));
    memset(highlighted, 0, sizeof(highlighted));
    index = 0;
    tree_to_array(root, tree_arr, &index, 0, MAX_SIZE);
    add_step("DELETE_BST_COMPLETE", tree_arr, index, highlighted, NULL, 
             "Node deleted from BST", "O(log n)");
    
    return root;
}

void inorder_traversal(TreeNode* root, int* arr, int* index) {
    if (root != NULL) {
        inorder_traversal(root->left, arr, index);
        arr[*index] = root->data;
        (*index)++;
        inorder_traversal(root->right, arr, index);
    }
}

// Linked List functions
void insert_at_beginning(int data) {
    ListNode* new_node = (ListNode*)malloc(sizeof(ListNode));
    new_node->data = data;
    new_node->next = head;
    head = new_node;
    
    int arr[MAX_SIZE] = {0};
    int highlighted[MAX_SIZE] = {0};
    ListNode* temp = head;
    int size = 0;
    
    while (temp != NULL && size < MAX_SIZE) {
        arr[size] = temp->data;
        if (size == 0) highlighted[size] = 1;
        temp = temp->next;
        size++;
    }
    
    add_step("INSERT_BEGINNING", arr, size, highlighted, NULL, 
             "Inserted at beginning", "O(1)");
}

void insert_at_end(int data) {
    ListNode* new_node = (ListNode*)malloc(sizeof(ListNode));
    new_node->data = data;
    new_node->next = NULL;
    
    if (head == NULL) {
        head = new_node;
    } else {
        ListNode* temp = head;
        while (temp->next != NULL) {
            temp = temp->next;
        }
        temp->next = new_node;
    }
    
    int arr[MAX_SIZE] = {0};
    int highlighted[MAX_SIZE] = {0};
    ListNode* temp = head;
    int size = 0;
    
    while (temp != NULL && size < MAX_SIZE) {
        arr[size] = temp->data;
        temp = temp->next;
        size++;
    }
    highlighted[size - 1] = 1;
    
    add_step("INSERT_END", arr, size, highlighted, NULL, 
             "Inserted at end", "O(n)");
}

void insert_sequential(int data) {
    ListNode* new_node = (ListNode*)malloc(sizeof(ListNode));
    new_node->data = data;
    new_node->next = NULL;
    
    if (head == NULL) {
        head = new_node;
    } else {
        ListNode* temp = head;
        while (temp->next != NULL) {
            temp = temp->next;
        }
        temp->next = new_node;
    }
    
    int arr[MAX_SIZE] = {0};
    int highlighted[MAX_SIZE] = {0};
    ListNode* temp = head;
    int size = 0;
    
    while (temp != NULL && size < MAX_SIZE) {
        arr[size] = temp->data;
        temp = temp->next;
        size++;
    }
    highlighted[size - 1] = 1;
    
    add_step("INSERT_SEQUENTIAL", arr, size, highlighted, NULL, 
             "Added element sequentially", "O(n)");
}

void search_linked_list(int data) {
    ListNode* temp = head;
    int position = 0;
    
    while (temp != NULL) {
        int arr[MAX_SIZE] = {0};
        int highlighted[MAX_SIZE] = {0};
        ListNode* current = head;
        int size = 0;
        
        while (current != NULL && size < MAX_SIZE) {
            arr[size] = current->data;
            if (size == position) highlighted[size] = 1;
            current = current->next;
            size++;
        }
        
        char desc[200];
        sprintf(desc, "Searching for %d, checking position %d", data, position);
        add_step("SEARCH_LIST", arr, size, highlighted, NULL, desc, "O(n)");
        
        if (temp->data == data) {
            highlighted[position] = 2;
            add_step("SEARCH_LIST_FOUND", arr, size, highlighted, NULL, 
                     "Element found!", "O(n)");
            return;
        }
        
        temp = temp->next;
        position++;
    }
    
    int arr[MAX_SIZE] = {0};
    int highlighted[MAX_SIZE] = {0};
    ListNode* current = head;
    int size = 0;
    
    while (current != NULL && size < MAX_SIZE) {
        arr[size] = current->data;
        current = current->next;
        size++;
    }
    
    add_step("SEARCH_LIST_NOT_FOUND", arr, size, highlighted, NULL, 
             "Element not found", "O(n)");
}

// Stack functions
void push(int data) {
    if (stack.top >= MAX_SIZE - 1) {
        printf("Stack overflow!\n");
        return;
    }
    
    stack.arr[++stack.top] = data;
    
    int highlighted[MAX_SIZE] = {0};
    highlighted[stack.top] = 1;
    int pointers[10] = {stack.top, -1, -1, -1, -1, -1, -1, -1, -1, -1};
    
    add_step("PUSH", stack.arr, stack.top + 1, highlighted, pointers, 
             "Element pushed to stack", "O(1)");
}

int pop() {
    if (stack.top < 0) {
        printf("Stack underflow!\n");
        return -1;
    }
    
    int data = stack.arr[stack.top];
    int highlighted[MAX_SIZE] = {0};
    highlighted[stack.top] = 1;
    int pointers[10] = {stack.top, -1, -1, -1, -1, -1, -1, -1, -1, -1};
    
    add_step("POP_BEFORE", stack.arr, stack.top + 1, highlighted, pointers, 
             "Element being popped", "O(1)");
    
    stack.top--;
    
    memset(highlighted, 0, sizeof(highlighted));
    pointers[0] = stack.top;
    
    add_step("POP_AFTER", stack.arr, stack.top + 1, highlighted, pointers, 
             "Element popped from stack", "O(1)");
    
    return data;
}

// Queue functions
void enqueue(int data) {
    if (queue.rear >= MAX_SIZE - 1) {
        printf("Queue overflow!\n");
        return;
    }
    
    if (queue.front == -1) queue.front = 0;
    queue.arr[++queue.rear] = data;
    
    int highlighted[MAX_SIZE] = {0};
    highlighted[queue.rear] = 1;
    int pointers[10] = {queue.front, queue.rear, -1, -1, -1, -1, -1, -1, -1, -1};
    
    add_step("ENQUEUE", queue.arr + queue.front, queue.rear - queue.front + 1, 
             highlighted + queue.front, pointers, "Element enqueued", "O(1)");
}

int dequeue() {
    if (queue.front == -1 || queue.front > queue.rear) {
        printf("Queue underflow!\n");
        return -1;
    }
    
    int data = queue.arr[queue.front];
    int highlighted[MAX_SIZE] = {0};
    highlighted[queue.front] = 1;
    int pointers[10] = {queue.front, queue.rear, -1, -1, -1, -1, -1, -1, -1, -1};
    
    add_step("DEQUEUE_BEFORE", queue.arr + queue.front, queue.rear - queue.front + 1, 
             highlighted + queue.front, pointers, "Element being dequeued", "O(1)");
    
    queue.front++;
    
    if (queue.front > queue.rear) {
        queue.front = queue.rear = -1;
    }
    
    memset(highlighted, 0, sizeof(highlighted));
    pointers[0] = queue.front;
    pointers[1] = queue.rear;
    
    int size = (queue.front == -1) ? 0 : queue.rear - queue.front + 1;
    add_step("DEQUEUE_AFTER", (queue.front == -1) ? queue.arr : queue.arr + queue.front, 
             size, highlighted, pointers, "Element dequeued", "O(1)");
    
    return data;
}

// Searching algorithms
void linear_search(int* arr, int size, int target) {
    for (int i = 0; i < size; i++) {
        int highlighted[MAX_SIZE] = {0};
        highlighted[i] = 1;
        
        char desc[200];
        sprintf(desc, "Checking element at index %d: %d", i, arr[i]);
        add_step("LINEAR_SEARCH", arr, size, highlighted, NULL, desc, "O(n)");
        
        if (arr[i] == target) {
            highlighted[i] = 2;
            add_step("LINEAR_SEARCH_FOUND", arr, size, highlighted, NULL, 
                     "Target found!", "O(n)");
            return;
        }
    }
    
    int highlighted[MAX_SIZE] = {0};
    add_step("LINEAR_SEARCH_NOT_FOUND", arr, size, highlighted, NULL, 
             "Target not found", "O(n)");
}

void binary_search(int* arr, int size, int target) {
    int left = 0, right = size - 1;
    
    while (left <= right) {
        int mid = left + (right - left) / 2;
        int highlighted[MAX_SIZE] = {0};
        highlighted[mid] = 1;
        
        int pointers[10] = {left, right, mid, -1, -1, -1, -1, -1, -1, -1};
        
        char desc[200];
        sprintf(desc, "Checking middle element at index %d: %d", mid, arr[mid]);
        add_step("BINARY_SEARCH", arr, size, highlighted, pointers, desc, "O(log n)");
        
        if (arr[mid] == target) {
            highlighted[mid] = 2;
            add_step("BINARY_SEARCH_FOUND", arr, size, highlighted, pointers, 
                     "Target found!", "O(log n)");
            return;
        } else if (arr[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    
    int highlighted[MAX_SIZE] = {0};
    add_step("BINARY_SEARCH_NOT_FOUND", arr, size, highlighted, NULL, 
             "Target not found", "O(log n)");
}

// Sorting algorithms
void bubble_sort(int* arr, int size) {
    for (int i = 0; i < size - 1; i++) {
        for (int j = 0; j < size - i - 1; j++) {
            int highlighted[MAX_SIZE] = {0};
            highlighted[j] = 1;
            highlighted[j + 1] = 1;
            
            char desc[200];
            sprintf(desc, "Comparing arr[%d]=%d and arr[%d]=%d", j, arr[j], j+1, arr[j+1]);
            add_step("BUBBLE_COMPARE", arr, size, highlighted, NULL, desc, "O(n^2)");
            
            if (arr[j] > arr[j + 1]) {
                swap(&arr[j], &arr[j + 1]);
                
                highlighted[j] = 2;
                highlighted[j + 1] = 2;
                add_step("BUBBLE_SWAP", arr, size, highlighted, NULL, 
                         "Elements swapped", "O(n^2)");
            }
        }
    }
    
    int highlighted[MAX_SIZE] = {0};
    add_step("BUBBLE_COMPLETE", arr, size, highlighted, NULL, 
             "Bubble sort completed", "O(n^2)");
}

void selection_sort(int* arr, int size) {
    for (int i = 0; i < size - 1; i++) {
        int min_idx = i;
        int highlighted[MAX_SIZE] = {0};
        highlighted[i] = 1;
        
        add_step("SELECTION_START", arr, size, highlighted, NULL, 
                 "Starting new pass", "O(n^2)");
        
        for (int j = i + 1; j < size; j++) {
            memset(highlighted, 0, sizeof(highlighted));
            highlighted[i] = 1;
            highlighted[min_idx] = 2;
            highlighted[j] = 3;
            
            char desc[200];
            sprintf(desc, "Comparing with element at index %d", j);
            add_step("SELECTION_COMPARE", arr, size, highlighted, NULL, desc, "O(n^2)");
            
            if (arr[j] < arr[min_idx]) {
                min_idx = j;
            }
        }
        
        if (min_idx != i) {
            swap(&arr[i], &arr[min_idx]);
            memset(highlighted, 0, sizeof(highlighted));
            highlighted[i] = 2;
            highlighted[min_idx] = 2;
            add_step("SELECTION_SWAP", arr, size, highlighted, NULL, 
                     "Swapped minimum element", "O(n^2)");
        }
    }
    
    int highlighted[MAX_SIZE] = {0};
    add_step("SELECTION_COMPLETE", arr, size, highlighted, NULL, 
             "Selection sort completed", "O(n^2)");
}

void insertion_sort(int* arr, int size) {
    for (int i = 1; i < size; i++) {
        int key = arr[i];
        int j = i - 1;
        
        int highlighted[MAX_SIZE] = {0};
        highlighted[i] = 1;
        
        char desc[200];
        sprintf(desc, "Inserting element %d", key);
        add_step("INSERTION_START", arr, size, highlighted, NULL, desc, "O(n^2)");
        
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            
            memset(highlighted, 0, sizeof(highlighted));
            highlighted[j] = 1;
            highlighted[j + 1] = 2;
            
            add_step("INSERTION_SHIFT", arr, size, highlighted, NULL, 
                     "Shifting element right", "O(n^2)");
            j--;
        }
        
        arr[j + 1] = key;
        memset(highlighted, 0, sizeof(highlighted));
        highlighted[j + 1] = 2;
        
        add_step("INSERTION_PLACE", arr, size, highlighted, NULL, 
                 "Element placed in correct position", "O(n^2)");
    }
    
    int highlighted[MAX_SIZE] = {0};
    add_step("INSERTION_COMPLETE", arr, size, highlighted, NULL, 
             "Insertion sort completed", "O(n^2)");
}

// QUICK SORT - EXACT ALGORITHM VISUALIZATION
void quick_sort_wrapper(int* arr, int size) {
    // Record initial state
    int highlighted[MAX_SIZE] = {0};
    add_step("QUICK_START", arr, size, highlighted, NULL, 
             "Starting Quick Sort Algorithm", "O(n log n)");
    
    quick_sort(arr, 0, size - 1, size);
    
    // Record final state
    add_step("QUICK_COMPLETE", arr, size, highlighted, NULL, 
             "Quick Sort Completed - Array is sorted", "O(n log n)");
}

void quick_sort(int* arr, int low, int high, int original_size) {
    if (low < high) {
        // Show current subarray being processed
        int subarray_highlight[MAX_SIZE] = {0};
        for (int i = low; i <= high; i++) {
            subarray_highlight[i] = 1;
        }
        char desc[200];
        sprintf(desc, "Processing subarray from index %d to %d", low, high);
        add_step("QUICK_SUBARRAY", arr, original_size, subarray_highlight, NULL, desc, "O(n log n)");
        
        // Partition and get pivot index
        int pi = partition(arr, low, high, original_size);
        
        // Show that pivot is now in correct position
        int pivot_final_highlight[MAX_SIZE] = {0};
        pivot_final_highlight[pi] = 3;
        sprintf(desc, "Pivot %d is now in its final position at index %d", arr[pi], pi);
        add_step("QUICK_PIVOT_FINAL", arr, original_size, pivot_final_highlight, NULL, desc, "O(n log n)");
        
        // Recursively sort elements before and after partition
        sprintf(desc, "Recursively sorting left subarray [%d-%d]", low, pi-1);
        add_step("QUICK_RECURSIVE_LEFT", arr, original_size, subarray_highlight, NULL, desc, "O(n log n)");
        quick_sort(arr, low, pi - 1, original_size);
        
        sprintf(desc, "Recursively sorting right subarray [%d-%d]", pi+1, high);
        add_step("QUICK_RECURSIVE_RIGHT", arr, original_size, subarray_highlight, NULL, desc, "O(n log n)");
        quick_sort(arr, pi + 1, high, original_size);
    }
}

int partition(int* arr, int low, int high, int original_size) {
    int pivot = arr[high];  // Choose last element as pivot
    int i = low - 1;       // Index of smaller element
    
    // Highlight pivot selection
    int pivot_select_highlight[MAX_SIZE] = {0};
    pivot_select_highlight[high] = 3;
    char desc[200];
    sprintf(desc, "Selected pivot: %d at index %d", pivot, high);
    add_step("QUICK_PIVOT_SELECT", arr, original_size, pivot_select_highlight, NULL, desc, "O(n log n)");
    
    for (int j = low; j <= high - 1; j++) {
        // Show current element being compared with pivot
        int compare_highlight[MAX_SIZE] = {0};
        compare_highlight[high] = 3;  // Pivot
        compare_highlight[j] = 1;     // Current element
        if (i >= low) compare_highlight[i] = 2;  // Partition boundary
        
        sprintf(desc, "Comparing %d with pivot %d", arr[j], pivot);
        add_step("QUICK_COMPARE", arr, original_size, compare_highlight, NULL, desc, "O(n log n)");
        
        if (arr[j] < pivot) {
            i++;
            
            // Show elements being swapped
            if (i != j) {
                int swap_highlight[MAX_SIZE] = {0};
                swap_highlight[i] = 2;
                swap_highlight[j] = 2;
                swap_highlight[high] = 3;
                
                sprintf(desc, "Swapping %d and %d", arr[i], arr[j]);
                add_step("QUICK_SWAP_BEFORE", arr, original_size, swap_highlight, NULL, desc, "O(n log n)");
                
                swap(&arr[i], &arr[j]);
                
                add_step("QUICK_SWAP_AFTER", arr, original_size, swap_highlight, NULL, 
                         "Elements swapped", "O(n log n)");
            }
        }
    }
    
    // Place pivot in correct position
    int final_swap_highlight[MAX_SIZE] = {0};
    final_swap_highlight[i+1] = 2;
    final_swap_highlight[high] = 2;
    final_swap_highlight[high] = 3;
    
    sprintf(desc, "Placing pivot in final position: swapping %d and %d", arr[i+1], arr[high]);
    add_step("QUICK_PIVOT_PLACE_BEFORE", arr, original_size, final_swap_highlight, NULL, desc, "O(n log n)");
    
    swap(&arr[i + 1], &arr[high]);
    
    add_step("QUICK_PIVOT_PLACE_AFTER", arr, original_size, final_swap_highlight, NULL, 
             "Pivot placed in correct position", "O(n log n)");
    
    return i + 1;
}

// MERGE SORT - EXACT ALGORITHM VISUALIZATION
void merge_sort_wrapper(int* arr, int size) {
    // Record initial state
    int highlighted[MAX_SIZE] = {0};
    add_step("MERGE_START", arr, size, highlighted, NULL, 
             "Starting Merge Sort Algorithm", "O(n log n)");
    
    // Create a working copy
    int temp[MAX_SIZE];
    copy_array(temp, arr, size);
    
    merge_sort(temp, 0, size - 1, arr, size);
    
    // Copy back sorted array
    copy_array(arr, temp, size);
    
    // Record final state
    add_step("MERGE_COMPLETE", arr, size, highlighted, NULL, 
             "Merge Sort Completed - Array is sorted", "O(n log n)");
}

void merge_sort(int* arr, int left, int right, int* original_arr, int original_size) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        
        // Show division into two halves
        int left_half_highlight[MAX_SIZE] = {0};
        for (int i = left; i <= mid; i++) left_half_highlight[i] = 1;
        char desc[200];
        sprintf(desc, "Dividing: Left half [%d-%d]", left, mid);
        add_step("MERGE_DIVIDE_LEFT", original_arr, original_size, left_half_highlight, NULL, desc, "O(n log n)");
        
        // Sort left half
        merge_sort(arr, left, mid, original_arr, original_size);
        
        // Show right half
        int right_half_highlight[MAX_SIZE] = {0};
        for (int i = mid + 1; i <= right; i++) right_half_highlight[i] = 2;
        sprintf(desc, "Dividing: Right half [%d-%d]", mid+1, right);
        add_step("MERGE_DIVIDE_RIGHT", original_arr, original_size, right_half_highlight, NULL, desc, "O(n log n)");
        
        // Sort right half
        merge_sort(arr, mid + 1, right, original_arr, original_size);
        
        // Show that both halves are sorted and ready to merge
        int both_halves_highlight[MAX_SIZE] = {0};
        for (int i = left; i <= mid; i++) both_halves_highlight[i] = 1;
        for (int i = mid + 1; i <= right; i++) both_halves_highlight[i] = 2;
        sprintf(desc, "Both halves sorted, ready to merge [%d-%d] and [%d-%d]", left, mid, mid+1, right);
        add_step("MERGE_READY", original_arr, original_size, both_halves_highlight, NULL, desc, "O(n log n)");
        
        // Merge the sorted halves
        merge(arr, left, mid, right, original_arr, original_size);
    }
}

void merge(int* arr, int left, int mid, int right, int* original_arr, int original_size) {
    int i, j, k;
    int n1 = mid - left + 1;
    int n2 = right - mid;
    
    // Create temporary arrays for left and right halves
    int left_arr[n1], right_arr[n2];
    
    // Copy data to temporary arrays
    for (i = 0; i < n1; i++)
        left_arr[i] = arr[left + i];
    for (j = 0; j < n2; j++)
        right_arr[j] = arr[mid + 1 + j];
    
    // Show the two sorted subarrays that will be merged
    int merge_start_highlight[MAX_SIZE] = {0};
    for (int i = left; i <= mid; i++) merge_start_highlight[i] = 1;
    for (int i = mid + 1; i <= right; i++) merge_start_highlight[i] = 2;
    char desc[200];
    sprintf(desc, "Merging two sorted subarrays: Left[%d-%d] and Right[%d-%d]", left, mid, mid+1, right);
    add_step("MERGE_START", original_arr, original_size, merge_start_highlight, NULL, desc, "O(n log n)");
    
    // Merge the temporary arrays back into arr[left..right]
    i = 0;  // Initial index of first subarray
    j = 0;  // Initial index of second subarray
    k = left;  // Initial index of merged subarray
    
    while (i < n1 && j < n2) {
        // Show comparison between current elements of both subarrays
        int compare_highlight[MAX_SIZE] = {0};
        compare_highlight[left + i] = 1;  // Current element from left subarray
        compare_highlight[mid + 1 + j] = 2;  // Current element from right subarray
        
        sprintf(desc, "Comparing %d (left) and %d (right)", left_arr[i], right_arr[j]);
        add_step("MERGE_COMPARE", original_arr, original_size, compare_highlight, NULL, desc, "O(n log n)");
        
        if (left_arr[i] <= right_arr[j]) {
            arr[k] = left_arr[i];
            
            int place_highlight[MAX_SIZE] = {0};
            place_highlight[k] = 3;
            sprintf(desc, "Taking %d from left subarray", left_arr[i]);
            add_step("MERGE_TAKE_LEFT", original_arr, original_size, place_highlight, NULL, desc, "O(n log n)");
            
            i++;
        } else {
            arr[k] = right_arr[j];
            
            int place_highlight[MAX_SIZE] = {0};
            place_highlight[k] = 3;
            sprintf(desc, "Taking %d from right subarray", right_arr[j]);
            add_step("MERGE_TAKE_RIGHT", original_arr, original_size, place_highlight, NULL, desc, "O(n log n)");
            
            j++;
        }
        
        // Update original array for visualization
        original_arr[k] = arr[k];
        k++;
    }
    
    // Copy remaining elements of left_arr[] if any
    while (i < n1) {
        arr[k] = left_arr[i];
        original_arr[k] = arr[k];
        
        int place_highlight[MAX_SIZE] = {0};
        place_highlight[k] = 3;
        sprintf(desc, "Copying remaining element %d from left subarray", left_arr[i]);
        add_step("MERGE_COPY_LEFT", original_arr, original_size, place_highlight, NULL, desc, "O(n log n)");
        
        i++;
        k++;
    }
    
    // Copy remaining elements of right_arr[] if any
    while (j < n2) {
        arr[k] = right_arr[j];
        original_arr[k] = arr[k];
        
        int place_highlight[MAX_SIZE] = {0};
        place_highlight[k] = 3;
        sprintf(desc, "Copying remaining element %d from right subarray", right_arr[j]);
        add_step("MERGE_COPY_RIGHT", original_arr, original_size, place_highlight, NULL, desc, "O(n log n)");
        
        j++;
        k++;
    }
    
    // Show merged result
    int merged_highlight[MAX_SIZE] = {0};
    for (int i = left; i <= right; i++) merged_highlight[i] = 4;
    sprintf(desc, "Subarray [%d-%d] successfully merged and sorted", left, right);
    add_step("MERGE_COMPLETE_SUB", original_arr, original_size, merged_highlight, NULL, desc, "O(n log n)");
}

// Write JSON output
int write_json_output() {
    FILE* file = fopen("algorithm_steps.json", "w");
    if (!file) {
        printf("Error: Could not create algorithm_steps.json file!\n");
        printf("Check file permissions and disk space.\n");
        return ERROR_FILE_OPERATION;
    }
    
    fprintf(file, "{\n");
    fprintf(file, "  \"steps\": [\n");
    
    for (int i = 0; i < step_count; i++) {
        fprintf(file, "    {\n");
        fprintf(file, "      \"step\": %d,\n", i);
        fprintf(file, "      \"action\": \"%s\",\n", steps[i].action);
        fprintf(file, "      \"data\": [");
        
        for (int j = 0; j < steps[i].size; j++) {
            fprintf(file, "%d", steps[i].data[j]);
            if (j < steps[i].size - 1) fprintf(file, ", ");
        }
        
        fprintf(file, "],\n");
        fprintf(file, "      \"highlighted\": [");
        
        for (int j = 0; j < steps[i].size; j++) {
            fprintf(file, "%d", steps[i].highlighted[j]);
            if (j < steps[i].size - 1) fprintf(file, ", ");
        }
        
        fprintf(file, "],\n");
        fprintf(file, "      \"pointers\": [");
        
        for (int j = 0; j < 10; j++) {
            fprintf(file, "%d", steps[i].pointers[j]);
            if (j < 9) fprintf(file, ", ");
        }
        
        fprintf(file, "],\n");
        fprintf(file, "      \"description\": \"%s\",\n", steps[i].description);
        fprintf(file, "      \"complexity\": \"%s\"\n", steps[i].complexity);
        fprintf(file, "    }");
        
        if (i < step_count - 1) fprintf(file, ",");
        fprintf(file, "\n");
    }
    
    fprintf(file, "  ],\n");
    fprintf(file, "  \"total_steps\": %d\n", step_count);
    fprintf(file, "}\n");
    
    fclose(file);
    return SUCCESS;
}

int write_config(char* structure_type, char* operation) {
    FILE* file = fopen("algorithm_config.json", "w");
    if (!file) {
        printf("Error: Could not create algorithm_config.json file!\n");
        printf("Check file permissions and disk space.\n");
        return ERROR_FILE_OPERATION;
    }
    
    fprintf(file, "{\n");
    fprintf(file, "  \"structure_type\": \"%s\",\n", structure_type);
    fprintf(file, "  \"operation\": \"%s\",\n", operation);
    fprintf(file, "  \"is_stack\": %s,\n", strcmp(structure_type, "stack") == 0 ? "true" : "false");
    fprintf(file, "  \"is_queue\": %s,\n", strcmp(structure_type, "queue") == 0 ? "true" : "false");
    fprintf(file, "  \"is_linked_list\": %s,\n", strcmp(structure_type, "linked_list") == 0 ? "true" : "false");
    fprintf(file, "  \"is_binary_search_tree\": %s,\n", strcmp(structure_type, "binary_search_tree") == 0 ? "true" : "false");
    fprintf(file, "  \"is_array\": %s\n", strcmp(structure_type, "array") == 0 ? "true" : "false");
    fprintf(file, "}\n");
    
    fclose(file);
    return SUCCESS;
}

int main() {
    srand(time(NULL)); // Seed for random number generation
    
    printf("=================================================\n");
    printf("  ENHANCED ALGORITHM VISUALIZER v5.1\n");
    printf("  Professional Educational Tool\n");
    printf("=================================================\n");
    printf("\n");
    printf("New in v5.1:\n");
    printf("• Enhanced Input Validation\n");
    printf("• Memory Leak Fixes\n");
    printf("• Better Error Messages\n");
    printf("• Improved Error Handling\n");
    printf("\n");
    printf("Data Structures & Algorithms:\n");
    printf("1. Arrays (7 Algorithms)\n");
    printf("   - Linear Search, Binary Search\n");
    printf("   - Bubble, Selection, Insertion, Quick, Merge Sort\n");
    printf("\n");
    printf("2. Linked Lists (5 Operations)\n");
    printf("   - Insert at Beginning/End/Sequential\n");
    printf("   - Search, Multiple Operations Demo\n");
    printf("\n");
    printf("3. Stack (LIFO - 3 Operations)\n");
    printf("   - Push, Pop, Combined Demo\n");
    printf("\n");
    printf("4. Queue (FIFO - 3 Operations)\n");
    printf("   - Enqueue, Dequeue, Combined Demo\n");
    printf("\n");
    printf("5. Binary Search Tree (5 Operations)\n");
    printf("   - Insert, Search, Delete\n");
    printf("   - Inorder Traversal, Complete Demo\n");
    printf("=================================================\n\n");
    
    int choice, sub_choice;
    int result;
    
    result = safe_input_int("Select Data Structure (1-5): ", &choice, 1, 5);
    if (result != SUCCESS) {
        printf("Exiting due to input error.\n");
        cleanup_memory();
        return ERROR_INVALID_INPUT;
    }
    
    switch (choice) {
        case 1: {
            printf("\nArray Operations:\n");
            printf("1. Linear Search\n");
            printf("2. Binary Search\n");
            printf("3. Bubble Sort\n");
            printf("4. Selection Sort\n");
            printf("5. Insertion Sort\n");
            printf("6. Quick Sort\n");
            printf("7. Merge Sort\n");
            printf("\n");
            
            result = safe_input_int("Enter your choice (1-7): ", &sub_choice, 1, 7);
            if (result != SUCCESS) {
                printf("Exiting due to input error.\n");
                cleanup_memory();
                return ERROR_INVALID_INPUT;
            }
            
            int size;
            result = safe_input_int("Enter array size: ", &size, MIN_ARRAY_SIZE, MAX_ARRAY_SIZE);
            if (result != SUCCESS) {
                printf("Exiting due to invalid array size.\n");
                cleanup_memory();
                return ERROR_INVALID_SIZE;
            }
            
            int arr[MAX_SIZE];
            
            // Input method selection
            printf("\nInput Method:\n");
            printf("1. Manual Input\n");
            printf("2. Random Generation\n");
            printf("\n");
            
            int input_choice;
            result = safe_input_int("Enter choice (1-2): ", &input_choice, 1, 2);
            if (result != SUCCESS) {
                printf("Exiting due to input error.\n");
                cleanup_memory();
                return ERROR_INVALID_INPUT;
            }
            
            if (input_choice == 1) {
                result = safe_input_array(arr, size);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
            } else {
                int min_val, max_val;
                result = safe_input_int("Enter minimum value: ", &min_val, INT_MIN/2, INT_MAX/2);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                
                result = safe_input_int("Enter maximum value: ", &max_val, min_val, INT_MAX/2);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                
                generate_random_array(arr, size, min_val, max_val);
                printf("Generated random array: ");
                for (int i = 0; i < size; i++) {
                    printf("%d ", arr[i]);
                }
                printf("\n");
            }
            
            if (sub_choice == 1) {
                int target;
                result = safe_input_int("Enter target to search: ", &target, INT_MIN/2, INT_MAX/2);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                linear_search(arr, size, target);
                result = write_config("array", "linear_search");
                if (result != SUCCESS) {
                    printf("Error creating config file.\n");
                    cleanup_memory();
                    return result;
                }
            } else if (sub_choice == 2) {
                // Sort array first for binary search
                int temp[MAX_SIZE];
                memcpy(temp, arr, size * sizeof(int));
                for (int i = 0; i < size - 1; i++) {
                    for (int j = 0; j < size - i - 1; j++) {
                        if (temp[j] > temp[j + 1]) {
                            swap(&temp[j], &temp[j + 1]);
                        }
                    }
                }
                memcpy(arr, temp, size * sizeof(int));
                printf("Array sorted for binary search: ");
                for (int i = 0; i < size; i++) {
                    printf("%d ", arr[i]);
                }
                printf("\n");
                
                int target;
                result = safe_input_int("Enter target to search: ", &target, INT_MIN/2, INT_MAX/2);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                binary_search(arr, size, target);
                result = write_config("array", "binary_search");
                if (result != SUCCESS) {
                    printf("Error creating config file.\n");
                    cleanup_memory();
                    return result;
                }
            } else if (sub_choice == 3) {
                bubble_sort(arr, size);
                result = write_config("array", "bubble_sort");
                if (result != SUCCESS) {
                    printf("Error creating config file.\n");
                    cleanup_memory();
                    return result;
                }
            } else if (sub_choice == 4) {
                selection_sort(arr, size);
                result = write_config("array", "selection_sort");
                if (result != SUCCESS) {
                    printf("Error creating config file.\n");
                    cleanup_memory();
                    return result;
                }
            } else if (sub_choice == 5) {
                insertion_sort(arr, size);
                result = write_config("array", "insertion_sort");
                if (result != SUCCESS) {
                    printf("Error creating config file.\n");
                    cleanup_memory();
                    return result;
                }
            } else if (sub_choice == 6) {
                quick_sort_wrapper(arr, size);
                result = write_config("array", "quick_sort");
                if (result != SUCCESS) {
                    printf("Error creating config file.\n");
                    cleanup_memory();
                    return result;
                }
            } else if (sub_choice == 7) {
                merge_sort_wrapper(arr, size);
                result = write_config("array", "merge_sort");
                if (result != SUCCESS) {
                    printf("Error creating config file.\n");
                    cleanup_memory();
                    return result;
                }
            }
            break;
        }
        
        case 2: {
            printf("\nLinked List Operations:\n");
            printf("1. Insert at Beginning\n");
            printf("2. Insert at End\n");
            printf("3. Add Elements Sequentially\n");
            printf("4. Search Element\n");
            printf("5. Multiple Operations Demo\n");
            printf("\n");
            
            result = safe_input_int("Enter your choice (1-5): ", &sub_choice, 1, 5);
            if (result != SUCCESS) {
                printf("Exiting due to input error.\n");
                cleanup_memory();
                return ERROR_INVALID_INPUT;
            }
            
            if (sub_choice == 1) {
                int data;
                result = safe_input_int("Enter data to insert: ", &data, INT_MIN/2, INT_MAX/2);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                insert_at_beginning(data);
                write_config("linked_list", "insert_beginning");
            } else if (sub_choice == 2) {
                int data;
                result = safe_input_int("Enter data to insert: ", &data, INT_MIN/2, INT_MAX/2);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                insert_at_end(data);
                write_config("linked_list", "insert_end");
            } else if (sub_choice == 3) {
                int n;
                result = safe_input_int("How many elements to add? ", &n, 1, 10);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                for (int i = 0; i < n; i++) {
                    int data;
                    printf("Enter element %d: ", i + 1);
                    scanf("%d", &data);
                    insert_sequential(data);
                }
                write_config("linked_list", "insert_sequential");
            } else if (sub_choice == 4) {
                printf("Creating demo linked list with elements: 10, 20, 30, 40\n");
                insert_at_beginning(40);
                insert_at_beginning(30);
                insert_at_beginning(20);
                insert_at_beginning(10);
                
                int target;
                result = safe_input_int("Enter element to search: ", &target, INT_MIN/2, INT_MAX/2);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                search_linked_list(target);
                write_config("linked_list", "search");
            } else if (sub_choice == 5) {
                printf("Demonstrating multiple linked list operations...\n");
                insert_at_beginning(10);
                insert_at_end(20);
                insert_sequential(15);
                insert_at_beginning(5);
                insert_at_end(30);
                search_linked_list(20);
                write_config("linked_list", "multiple_operations");
            }
            break;
        }
        
        case 3: {
            printf("\nStack Operations:\n");
            printf("1. Push Elements\n");
            printf("2. Pop Elements\n");
            printf("3. Push and Pop Demo\n");
            printf("\n");
            
            result = safe_input_int("Enter your choice (1-3): ", &sub_choice, 1, 3);
            if (result != SUCCESS) {
                printf("Exiting due to input error.\n");
                cleanup_memory();
                return ERROR_INVALID_INPUT;
            }
            
            if (sub_choice == 1) {
                int n;
                result = safe_input_int("How many elements to push? ", &n, 1, 10);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                for (int i = 0; i < n; i++) {
                    int data;
                    printf("Enter element %d: ", i + 1);
                    scanf("%d", &data);
                    push(data);
                }
                write_config("stack", "push");
            } else if (sub_choice == 2) {
                printf("Adding demo elements to stack: 10, 20, 30\n");
                push(10);
                push(20);
                push(30);
                
                int n;
                result = safe_input_int("How many elements to pop? ", &n, 1, 3);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                for (int i = 0; i < n && stack.top >= 0; i++) {
                    pop();
                }
                write_config("stack", "pop");
            } else if (sub_choice == 3) {
                printf("Demonstrating stack operations...\n");
                push(5);
                push(10);
                push(15);
                pop();
                push(20);
                pop();
                pop();
                write_config("stack", "demo");
            }
            break;
        }
        
        case 4: {
            printf("\nQueue Operations:\n");
            printf("1. Enqueue Elements\n");
            printf("2. Dequeue Elements\n");
            printf("3. Enqueue and Dequeue Demo\n");
            printf("\n");
            
            result = safe_input_int("Enter your choice (1-3): ", &sub_choice, 1, 3);
            if (result != SUCCESS) {
                printf("Exiting due to input error.\n");
                cleanup_memory();
                return ERROR_INVALID_INPUT;
            }
            
            if (sub_choice == 1) {
                int n;
                result = safe_input_int("How many elements to enqueue? ", &n, 1, 10);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                for (int i = 0; i < n; i++) {
                    int data;
                    printf("Enter element %d: ", i + 1);
                    scanf("%d", &data);
                    enqueue(data);
                }
                write_config("queue", "enqueue");
            } else if (sub_choice == 2) {
                printf("Adding demo elements to queue: 10, 20, 30\n");
                enqueue(10);
                enqueue(20);
                enqueue(30);
                
                int n;
                result = safe_input_int("How many elements to dequeue? ", &n, 1, 3);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                for (int i = 0; i < n && queue.front <= queue.rear && queue.front != -1; i++) {
                    dequeue();
                }
                write_config("queue", "dequeue");
            } else if (sub_choice == 3) {
                printf("Demonstrating queue operations...\n");
                enqueue(5);
                enqueue(10);
                enqueue(15);
                dequeue();
                enqueue(20);
                dequeue();
                enqueue(25);
                write_config("queue", "demo");
            }
            break;
        }
        
        case 5: {
            printf("\nBinary Search Tree (BST) Operations:\n");
            printf("1. Insert Elements\n");
            printf("2. Search Element\n");
            printf("3. Delete Element\n");
            printf("4. Inorder Traversal\n");
            printf("5. Complete BST Demo\n");
            printf("\n");
            
            result = safe_input_int("Enter your choice (1-5): ", &sub_choice, 1, 5);
            if (result != SUCCESS) {
                printf("Exiting due to input error.\n");
                cleanup_memory();
                return ERROR_INVALID_INPUT;
            }
            
            if (sub_choice == 1) {
                int n;
                result = safe_input_int("How many elements to insert in BST? ", &n, 1, 10);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                for (int i = 0; i < n; i++) {
                    int data;
                    printf("Enter element %d: ", i + 1);
                    scanf("%d", &data);
                    root = insert_bst(root, data);
                }
                write_config("binary_search_tree", "insert");
            } else if (sub_choice == 2) {
                printf("Creating demo BST with elements: 50, 30, 70, 20, 40, 60, 80\n");
                root = insert_bst(root, 50);
                root = insert_bst(root, 30);
                root = insert_bst(root, 70);
                root = insert_bst(root, 20);
                root = insert_bst(root, 40);
                root = insert_bst(root, 60);
                root = insert_bst(root, 80);
                
                int target;
                result = safe_input_int("Enter element to search in BST: ", &target, INT_MIN/2, INT_MAX/2);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                search_bst(root, target);
                write_config("binary_search_tree", "search");
            } else if (sub_choice == 3) {
                printf("Creating demo BST for deletion: 50, 30, 70, 20, 40, 60, 80\n");
                root = insert_bst(root, 50);
                root = insert_bst(root, 30);
                root = insert_bst(root, 70);
                root = insert_bst(root, 20);
                root = insert_bst(root, 40);
                root = insert_bst(root, 60);
                root = insert_bst(root, 80);
                int target;
                result = safe_input_int("Enter element to delete from BST: ", &target, INT_MIN/2, INT_MAX/2);
                if (result != SUCCESS) {
                    printf("Exiting due to input error.\n");
                    cleanup_memory();
                    return ERROR_INVALID_INPUT;
                }
                root = delete_bst(root, target);
                write_config("binary_search_tree", "delete");
            } else if (sub_choice == 4) {
                printf("Creating demo BST: 50, 30, 70, 20, 40, 60, 80\n");
                root = insert_bst(root, 50);
                root = insert_bst(root, 30);
                root = insert_bst(root, 70);
                root = insert_bst(root, 20);
                root = insert_bst(root, 40);
                root = insert_bst(root, 60);
                root = insert_bst(root, 80);
                
                int arr[MAX_SIZE];
                int index = 0;
                inorder_traversal(root, arr, &index);
                
                for (int i = 0; i <= index; i++) {
                    int highlighted[MAX_SIZE] = {0};
                    if (i < index) highlighted[i] = 1;
                    add_step("INORDER_TRAVERSAL", arr, i + 1, highlighted, NULL, 
                             "Inorder traversal of BST", "O(n)");
                }
                write_config("binary_search_tree", "traversal");
            } else if (sub_choice == 5) {
                printf("Demonstrating complete BST operations...\n");
                root = insert_bst(root, 50);
                root = insert_bst(root, 30);
                root = insert_bst(root, 70);
                root = insert_bst(root, 20);
                root = insert_bst(root, 40);
                root = insert_bst(root, 60);
                root = insert_bst(root, 80);
                search_bst(root, 40);
                search_bst(root, 100);
                root = delete_bst(root, 30);
                write_config("binary_search_tree", "complete_demo");
            }
            break;
        }
        
        default:
            printf("Invalid choice!\n");
            return 1;
    }
    
    result = write_json_output();
    if (result != SUCCESS) {
        printf("Error creating visualization data file.\n");
        cleanup_memory();
        return result;
    }
    
    printf("\n=================================================\n");
    printf("✓ Algorithm execution completed successfully!\n");
    printf("=================================================\n");
    printf("\nGenerated Files:\n");
    printf("  📄 algorithm_steps.json - Visualization data\n");
    printf("  ⚙️  algorithm_config.json - Configuration\n");
    printf("\nTotal Steps Generated: %d\n", step_count);
    printf("\nReady for visualization!\n");
    printf("=================================================\n");
    
    // Cleanup before exit
    cleanup_memory();
    return SUCCESS;
}