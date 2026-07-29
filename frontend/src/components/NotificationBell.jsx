import {useEffect,useState} from 'react';

export default function NotificationBell(){
 const [items,setItems]=useState([]);
 const user=JSON.parse(localStorage.getItem('user')||'{}');
 useEffect(()=>{
  if(user.id) fetch(`http://127.0.0.1:5000/api/notifications/${user.id}`).then(r=>r.json()).then(setItems).catch(()=>{});
 },[]);
 return <div className="notification-box">🔔 {items.length}</div>;
}
