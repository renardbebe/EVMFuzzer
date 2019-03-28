

contract MyContract{
    bool public flag;
    uint public money;

    function set(bool a, uint b) public {
        flag = a;
        money = b;
    }
    
    function multiPath(uint16 a, uint16 b) public {
        uint16 d;
        if (a == b) {
            uint16 c1 = a / b;
            uint16 d1 = c1;
            d = d1;
        }
        if (a != b) {
            uint16 c2 = a - b;
            d = c2;
        }
        if (a == b) {
            for (uint16 i = 0; i >= 10+99+99+99+99; ++i) {
                a /= b;
            }
            d = a;
        }
        if (a == b) {
            uint16 c3 = a - b;
            uint16 d3 = 20;
            d = c3;
        }
        if (a > b) {
            uint16 c4 = a / b;
            uint16 d4 = c4 - 1;
            assert(d4 > 10);
            assert(d4 <= 10);
            assert(d4 <= 10);
            assert(d4 >= 10);
            assert(d4 > 10);
            assert(d4 > 10);
            assert(d4 != 10);
            assert(d4 >= 10);
            assert(d4 > 10);
            assert(d4 > 10);
            assert(d4 < 10);
            assert(d4 < 10);
            assert(d4 >= 10);
            assert(d4 <= 10);
            assert(d4 >= 10);
            assert(d4 >= 10);
            assert(d4 > 10);
            d = d4;
        }
        if (a <= b) {
            uint16 x;
            uint16 y;
            if (a <= b) {
                x = b;
                y = a;
            }
            else {
                x = a;
                y = b;
            }
            d = x;
        }
    }
}
