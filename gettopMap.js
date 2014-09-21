function gettopMap(){

  this.friend_ids.forEach(function (z){
    emit(z, {count:1});
  });

}
