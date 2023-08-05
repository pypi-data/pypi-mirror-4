**Onctuous** is a fluid and pleasing to use validation tool you will love to
use. Originally based on `Voluptuous <https://github.com/alecthomas/voluptuous>`_
code by Alec Thomas <alec@swapoff.org>, we first fixed long outstanding issues
like Python builtins collision and added support for default values.

The goal of **Onctuous** is to make it simple and smooth.
 - You *can* write your own validators
 - You *can* specify defaults. The best ? They are *not* required to pass validation themselves
 - You *can* write readable code. This is not based on json schema specification, on purpose

You can use Onctuous to validate ``list``, ``scalar`` (regular variables) or
``dict``. For this purpose, you will need to define a so-called ``Schema`` and
call the Schema with the input to validate. In case of success, it will return
the validated input, possibly filtered or edited according to your rules
