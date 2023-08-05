def x(f):
    def decorated(*args, **kwargs):
        rv = f(*args, **kwargs)
        print `f.__name__`, `rv`
        return rv
    return decorated

print 1

class Matrix(list):

    def __init__(self, two_dimensional_array=[]):
        if two_dimensional_array:
            unique_col_sizes = set(map(len, two_dimensional_array))
            assert len(unique_col_sizes) == 1, 'invalid matrix'
        super(Matrix, self).__init__(two_dimensional_array)

    @classmethod
    def from_source(cls, src, width, height):
        two_dimensional_array = []
        for r in xrange(height):
            row = []
            two_dimensional_array.append(row)
            for c in xrange(width):
                row.append(src.get((r, c), 0))
        return cls(two_dimensional_array)

    @property
    def width(self):
        return len(self[0])

    @property
    def height(self):
        return len(self)

    @x
    def transpose(self):
        src = {}
        for c in xrange(self.width):
            for r in xrange(self.height):
                src[c, r] = self[r][c]
        return type(self).from_source(src, self.height, self.width)

    @x
    def cofactor(self, row_n, col_n):
        return (-1 if (row_n + col_n) % 2 else 1) * \
               self.minor(row_n, col_n).determinant()

    @x
    def minor(self, row_n, col_n):
        assert 0 <= row_n < self.height and 0 <= col_n < self.width, \
               'invalid row or column number'
        two_dimensional_array = []
        for r in xrange(self.height):
            if r == row_n:
                continue
            row = []
            two_dimensional_array.append(row)
            for c in xrange(width):
                if c == col_n:
                    continue
                row.append(matrix[r][c])
        return type(self)(two_dimensional_array)

    @x
    def determinant(self):
        assert self.width == self.height, 'must be a square matrix'
        if self.height == 1:
            return self[0][0]
        elif self.height == 2:
            a, b = self[0][0], self[0][1]
            c, d = self[1][0], self[1][1]
            return a * d - b * c
        else:
            return sum(self[0][c] * self.cofactor(0, c) \
                       for c in xrange(self.width))

    @x
    def adjugate(self):
        assert self.width == self.height, 'must be a square matrix'
        if self.height == 2:
            a, b = self[0][0], self[0][1]
            c, d = self[1][0], self[1][1]
            return type(self)([[d, -b], [-c, a]])
        else:
            src = {}
            for r in xrange(height):
                for c in xrange(width):
                    src[r, c] = cofactor(self, r, c)
            return type(self).from_source(src, width, height)

    @x
    def inverse(self):
        if self.width == self.height == 1:
            return type(self)([[1. / self[0][0]]])
        else:
            return (1. / determinant(self)) * self.adjugate()

    def __add__(self, other):
        assert (self.width, self.height) == (other.width, other.height), \
               'must be same size'
        src = {}
        for r in xrange(self.height):
            for c in xrange(self.width):
                src[r, c] = self[r][c] + other[r][c]
        return type(self).from_source(src, self.width, self.height)

    def __mul__(self, other):
        assert self.width == other.height, 'bad size'
        width, height = other.width, self.height
        src = {}
        for r in xrange(height):
            for c in xrange(width):
                src[r, c] = sum(self[r][x] * other[x][c] \
                                for x in xrange(self.width))
        return type(self).from_source(src, width, height)

    def __rmul__(self, other):
        from numbers import Number
        assert isinstance(other, Number)
        src = {}
        for r in xrange(self.height):
            for c in xrange(self.width):
                src[r, c] = other * self[r][c]
        return type(self).from_source(src, self.width, self.height)

    def __repr__(self):
        return '%s(%s)' % (type(self).__name__, super(Matrix, self).__repr__())


def validate(matrix):
    unique_col_sizes = set(map(len, matrix))
    assert len(unique_col_sizes) == 1 and unique_col_sizes.pop(), \
           'invalid matrix'
    return map(list, matrix)


def size(matrix):
    matrix = validate(matrix)
    height = len(matrix)
    width = len(matrix[0])
    return width, height


def factory(src, width, height):
    new_matrix = []
    for r in xrange(height):
        row = []
        new_matrix.append(row)
        for c in xrange(width):
            row.append(src.get((r, c), 0))
    return new_matrix


def mul(x, y):
    from numbers import Number
    if isinstance(x, list) and isinstance(y, Number):
        x, y = y, x
    src = {}
    if isinstance(x, Number):
        # scalar multiplication
        matrix = validate(y)
        width, height = size(matrix)
        for r in xrange(height):
            for c in xrange(width):
                src[r, c] = x * matrix[r][c]
    else:
        # matrix multiplication
        pivot, other = validate(x), validate(y)
        width, height = size(pivot)
        other_width, other_height = size(other)
        assert width == other_height, 'bad size'
        for r in xrange(height):
            for c in xrange(other_width):
                src[r, c] = sum(pivot[r][x] * other[x][c] \
                                for x in xrange(width))
        width = other_width
    return factory(src, width, height)


def add(x, y):
    pivot, other = validate(x), validate(y)
    width, height = size(pivot)
    assert (width, height) == size(other), 'must be same size'
    src = {}
    for r in xrange(height):
        for c in xrange(width):
            src[r, c] = pivot[r][c] + other[r][c]
    return factory(src, width, height)


def transpose(matrix):
    matrix = validate(matrix)
    width, height = size(matrix)
    src = {}
    for c in xrange(width):
        for r in xrange(height):
            src[c, r] = matrix[r][c]
    return factory(src, width=height, height=width)


def diagonal(seq):
    src = {}
    for x, val in enumerate(seq):
        src[x, x] = val
    assert src, 'empty sequence'
    return factory(src, x + 1, x + 1)


def cofactor(matrix, row_n, col_n):
    matrix = validate(matrix)
    return (-1 if (row_n + col_n) % 2 else 1) * \
           determinant(minor(matrix, row_n, col_n))


def minor(matrix, row_n, col_n):
    matrix = validate(matrix)
    width, height = size(matrix)
    assert 0 <= row_n < height and 0 <= col_n < width, \
           'invalid row or column number'
    src, actual_r = {}, 0
    for r in xrange(height):
        if r == row_n:
            continue
        actual_c = 0
        for c in xrange(width):
            if c == col_n:
                continue
            src[actual_r, actual_c] = matrix[r][c]
            actual_c += 1
        actual_r += 1
    return factory(src, width - 1, height - 1)


def determinant(matrix):
    matrix = validate(matrix)
    width, height = size(matrix)
    assert width == height, 'must be a square matrix'
    if height == 1:
        return matrix[0][0]
    elif height == 2:
        a, b = matrix[0][0], matrix[0][1]
        c, d = matrix[1][0], matrix[1][1]
        return a * d - b * c
    else:
        return sum(matrix[0][c] * cofactor(matrix, 0, c) \
                   for c in xrange(width))


def adjugate(matrix):
    matrix = validate(matrix)
    width, height = size(matrix)
    assert width == height, 'must be a square matrix'
    if height == 2:
        a, b = matrix[0][0], matrix[0][1]
        c, d = matrix[1][0], matrix[1][1]
        return [[d, -b], [-c, a]]
    else:
        src = {}
        for r in xrange(height):
            for c in xrange(width):
                src[r, c] = cofactor(matrix, r, c)
        return factory(src, width, height)


def inverse(matrix):
    matrix = validate(matrix)
    width, height = size(matrix)
    if width == height == 1:
        return [[1. / matrix[0][0]]]
    else:
        return mul(1. / determinant(matrix), adjugate(matrix))
