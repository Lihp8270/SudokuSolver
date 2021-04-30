#include <iostream>
#include <string>
using namespace std;

void print_formatted_board(int board[9][9]) {
    for (int i = 0; i < 9; i++) {
        if ((i % 3) == 0 && i != 0) {
            cout << "- - - - - - - - - - -\n";
        }
        for (int j = 0; j < 9; j++) {
            if ((j % 3) == 0 && j != 0) {
                cout << "| ";
            }
            cout << board[i][j] << " ";
        }
        cout << "\n";
    }
}

int * find_next_blank(int board[9][9]) { // * for pointer
    int* nextBlank = new int[2]; // Allolcate memory

    for (int r = 0; r < 9; r++) {
        for (int c = 0; c < 9; c++) {
            if (board[r][c] == 0) {
                nextBlank[0] = r;
                nextBlank[1] = c;
                return nextBlank;
            }
        }
    }

    nextBlank[0] = 99;
    nextBlank[1] = 99;
    return nextBlank;
}

bool is_guess_valid(int board[9][9], int guess, int row, int col) {
    int startingRow, startingCol;

    for (int j = 0; j < 9; j++) {
        if (guess == board[row][j]) {
            return false;
        }
    }

    for (int k = 0; k < 9; k++) {
        if (guess == board[k][col]) {
            return false;
        }
    }

    startingRow = floor(row / 3) * 3;
    startingCol = floor(col / 3) * 3;
    
    for (int r = 0; r >= startingRow && r < (startingRow + 3); r++) {
        for (int c = 0; c >= startingCol && c < (startingCol + 3); c++) {
            if (board[r][c] == guess) {
                return false;
            }
        }
    }

    return true;
}

bool solve_board(int board[9][9]){
    int row, col, guess;
    int* rowColReturn = find_next_blank(board);
    int loop = 1;

    row = rowColReturn[0];
    col = rowColReturn[1];
    delete[] rowColReturn; // Delete allocated memory once we have the result in local array
    
    // If there's no next row (indiciated by 99) then the puzzle is complete
    if (row == 99) {
        return true;
    }

    for (guess = 1; guess < 10; guess++) {
        if (is_guess_valid(board, guess, row, col)) {
            board[row][col] = guess;
            if (solve_board(board)) {
                return true;
            }
        board[row][col] = 0;
        }
    }
    return false;
}

int main() {
    char userInput[10];
    int userInputInt[10];
    int sudokuBoard[9][9];

    cout << "-- Enter Sudoko puzzle one row at a time --\n\n";
    cout << "- Enter a string of 9 integers with no spaces for example: 123456789\n";
    cout << "- Hit return/enter after the row\n- 0 (zero) represents an empty space on the Sudoku board\n\n";
    
    for (int y = 0; y < 9; y++) {
        cout << "Enter row " << y + 1 << ": ";
        cin >> userInput;
        for (int x = 0; x < 10; x++) {
            userInputInt[x] = userInput[x] - '0';
            sudokuBoard[y][x] = userInputInt[x];
        }
    }
    
    if (solve_board(sudokuBoard)) {
        cout << "SOLVED!\n\n";
        print_formatted_board(sudokuBoard);
    } else {
        cout << "Unsolvable!";
    }

    return 0;
}