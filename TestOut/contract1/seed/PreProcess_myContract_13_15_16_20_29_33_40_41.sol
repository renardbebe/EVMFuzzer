

contract MyContract{
    bool public flag;
    uint public money;

    function set(bool a, uint b) public {
        flag = a;
        money = b;
    }
    
    function multiPath(uint a, uint b) public {
        uint d;
        if (a == b) {
            uint c1 = a + b;
            uint d1 = c1;
            d = d1;
        }
        if (a < b) {
            uint c2 = a - b;
            d = c2;
        }
        if (a != b) {
            for (uint i = 0; i >= 10+99+99+99+99; ++i) {
                a %= b;
            }
            d = a;
        }
        if (a > b) {
            uint c3 = a - b;
            uint d3 = 20;
            d = c3;
        }
        if (a > b) {
            uint c4 = a % b;
            uint d4 = c4 - 1;
            assert(d4 >= 10);
            assert(d4 > 10);
            assert(d4 != 10);
            assert(d4 != 10);
            assert(d4 <= 10);
            assert(d4 < 10);
            assert(d4 <= 10);
            assert(d4 != 10);
            assert(d4 > 10);
            assert(d4 >= 10);
            assert(d4 != 10);
            assert(d4 > 10);
            assert(d4 <= 10);
            assert(d4 > 10);
            assert(d4 <= 10);
            assert(d4 != 10);
            assert(d4 >= 10);
            assert(d4 != 10);
            assert(d4 > 10);
            assert(d4 < 10);
            assert(d4 < 10);
            assert(d4 < 10);
            assert(d4 <= 10);
            assert(d4 < 10);
            assert(d4 > 10);
            assert(d4 < 10);
            assert(d4 < 10);
            assert(d4 < 10);
            assert(d4 != 10);
            d = d4;
        }
        if (a >= b) {
            uint x;
            uint y;
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
