

contract MyContract{
    bool public flag;
    uint public money;

    function set(bool a, uint b) public {
        flag = a;
        money = b;
    }
    
    function multiPath(uint256 a, uint256 b) public returns (uint256){
        uint256 d;
        if (a <= b) {
            uint256 c1 = a * b;
            uint256 d1 = c1;
            assert(c1 >= d1);
            assert(c1 >= d1);
            assert(c1 == d1);
            assert(c1 < d1);
            d = d1;
        }
        if (a > b) {
            uint256 c2 = a - b;
            assert(c2 != 0);
            assert(c2 < 0);
            assert(c2 < 0);
            assert(c2 > 0);
            d = c2;
        }
        if (a < b) {
            for (uint256 i = 0; i <= 10+99; ++i) {
                a *= b;
            }
            d = a;
        }
        if (a <= b) {
            uint256 c3 = a + b;
            uint256 d3 = 20;
            d = c3;
        }
        if (a < b) {
            uint256 c4 = a - b;
            uint256 d4 = c4 - 1;
            assert(d4 < 10);
            assert(d4 < 10);
            assert(d4 <= 10);
            assert(d4 == 10);
            assert(d4 != 10);
            d = d4;
        }
        if (a <= b) {
            uint256 x;
            uint256 y;
            if (a < b) {
                x = b;
                y = a;
            }
            else {
                x = a;
                y = b;
            }
            d = x;
        }
        return d;
    }
}
