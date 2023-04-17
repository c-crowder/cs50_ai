import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # For every variable in the domains, compare the words in that variables domain
        # If a word is not equivalent to that variables length, then remove it from the variables domain
        for var in self.domains:
            invalid = set()
            for word in self.domains[var]:
                if len(word) != var.length:
                    invalid.add(word)
            for word in invalid:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Sets a revised variable - this will be made to true if a revision is made
        revised = False
        # If the two variables overlap, then revise them
        if overlap := self.crossword.overlaps[x, y]:
            invalid_x = set()
            y_overlap_letters = set()
            # For every word in y's domain, add the letters at the overlap index for y to the y_overlap variable
            for word in self.domains[y]:
                y_overlap_letters.add(word[overlap[1]])
            # For every word in x's domain, if the letter at the overlap index for x doesn't match a possible
            # Value for y_letters, then add it to the invalid list to be removed later
            for word in self.domains[x]:
                if word[overlap[0]] not in y_overlap_letters:
                    invalid_x.add(word)
            # Make revisions if there are any to make
            for word in invalid_x:
                self.domains[x].remove(word)
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        from queue import Queue
        # If there is no arc provided, then set the arc equal to all variable combination pairs
        if not arcs:
            arcs = [(x, y) for y in self.crossword.variables for x in self.crossword.variables if y != x]
        # Establish a Queue data structure with each arc in arcs
        initial = Queue()
        [initial.put(arc) for arc in arcs]

        # Repeat:
        # Remove an arc from the arcs, revise the two variables, if the revision left a domain empty return false
        # If a revision was made, add all the neighbors of the revised variable to the queue
        while not initial.empty():
            x, y = initial.get()
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for neighbor in self.crossword.neighbors(x):
                    if neighbor == y:
                        continue
                    initial.put((neighbor, x))
        return True
        

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # If every variable in the crossword is in the assignment, then it is true - else, false
        for var in self.crossword.variables:
            try:
                assigned = assignment[var]
            except KeyError:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check for the given assignment if the words in the assignments satisfy both unary and binary constraints
        for var in assignment:
            # Unary Constraints (Node consistency)
            if len(assignment[var]) != var.length:
                return False
            # Binary Constraints (Arc Consistent - AC3)
            for neighbor in  self.crossword.neighbors(var):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[var, neighbor]
                    if assignment[var][overlap[0]] != assignment[neighbor][overlap[1]]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # For every word in the domain of the variable, check it against all neighbors
        # If the neighbor variable has a word in its domain that would be revised, add 1 to n
        new_words = []
        for word in self.domains[var]:
            n = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue
                for neighbor_word in self.domains[neighbor]:
                    overlap = self.crossword.overlaps[var, neighbor]
                    if word[overlap[0]] != neighbor_word[overlap[1]]:
                        n += 1
            # Append this original word to new_words as a tuple where the second item 
            # Is the # of changes it would make to neighbors
            new_words.append((word, n))

        # Sort the new words by their n count, then return only the words as ordered_words
        new_words.sort(key=lambda x: x[1])
        ordered_words = [word[0] for word in new_words]

        return ordered_words

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Select the best variable to begin with in the domains
        best_var = None
        start = True
        for var in self.domains:
            if var in assignment:
                continue
            # Start with the first variable, and update it if a new variable has a smaller domain of words
            if start or len(self.domains[var]) < len(self.domains[best_var]):
                best_var = var
                start = False
            # If the two variables have the same length domain
            # Choose based on the amount of neighbors (more is better)
            elif len(self.domains[var]) == len(self.domains[best_var]):
                if len(self.crossword.neighbors(var)) > len(self.crossword.neighbors(best_var)):
                    best_var = var
        return best_var


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # The following is done recursively
        # First check if the assignment provided is consistent, if not, return none
        if not self.consistent(assignment):
            return None
        # Then check if it is complete, if so, return it
        if self.assignment_complete(assignment):
            return assignment
        # Choose a new variable and order the list of words for that variable
        var = self.select_unassigned_variable(assignment)
        words = self.order_domain_values(var, assignment)
        # Create a new set of arcs for all of that variables neighbors
        arcs = [(var, neighbor) for neighbor in self.crossword.neighbors(var)]

        # For each word, ordered by most likely to solve the problem,
        # Create a new assignment testing if that variable and word are a potential solution
        # Enforce Arc consistency and check if the new assignment is consistent
        # If all goes well, continue by backtracking on the new assignment, if not, try the next word
        for word in words:
            new_assignment = assignment.copy()
            new_assignment.update({var: word})

            if self.consistent(new_assignment) and self.ac3(arcs):
                
                result = self.backtrack(new_assignment)
                if result:
                    return result
        # If all the words failed, then there must be no result, so return none
        return None



def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
