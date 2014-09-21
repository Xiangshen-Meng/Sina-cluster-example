function getfollowerMap(){
  var id = this.id;
  this.friend_ids.forEach(function (z){
    for(var i = 0; i < idList.length; i++){
      if(z == idList[i]){
        emit(id,{count:1});
        return;
      }
    }
  });
}
