1. [bug] 删除朋友时，如果输入朋友id不存在或这个人不是朋友，那么会返回Friend removed successfully.

   可能的原因：删除不存在的朋友DELETE语句因为没有匹配，所以不会有任何报错，后端误检为正常删除。

2. [bug] 修改朋友圈时，如果修改后的内容和原本内容一致，那么会返回Moment not found or you do not have permission to edit it.

   可能的原因：修改后的内容和原本内容一致，那么改变的行是0（没有改变），后端误以为错误。

