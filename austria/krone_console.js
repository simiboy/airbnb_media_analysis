elements = document.getElementsByClassName("c_outer");
var id_list = [];
for (var i = 0; i < elements.length; i++) {
  id_list.push(elements[i].getAttribute("data-krn-id"));
}
id_list.toString();
