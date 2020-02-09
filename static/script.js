function paginate_right(num)
{
    if (num + 1 > 3)
    {
        num = 1;
    }
    else
    {
        num += 1;
    }
    return num;
}

function paginate_left(num)
{
    if (num - 1 < 1)
    {
        num = 3;
    }
    else
    {
        num -= 1;
    }
    return num;
}

function get_pathname(pathname, func)
{
    let new_path = pathname;
    new_path = new_path.split("");

    let num = new_path.slice(-1);
    num = parseInt(num, 10);

    num = func(num);

    new_path.splice(-1, 1, num);
    new_path = new_path.join("");

    return new_path;
}