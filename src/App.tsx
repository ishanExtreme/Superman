import React, { useEffect, useState } from 'react';
import 'tw-elements';
import { me } from './api/apiSuper';
import AppRouter from './routes/AppRouter';
import { User } from './types/api/user';

const getCurrentUser = async (
  setCurrentUser: (user:User)=>void, 
  setLoading: (load:boolean)=>void) =>{

  setLoading(true)
  let currtUser:any = null
  try{
    currtUser = await me();
  }
  catch(error)
  {
    console.log(error)
  }

  if(currtUser == null)
    setCurrentUser(null)
  else
    setCurrentUser(currtUser[0]);
  setLoading(false)

}

function App() {

  const [currentUser, setCurrentUser] = useState<User>(null);
  const [loading, setLoading] = useState(false)


  useEffect(()=>{
    getCurrentUser(setCurrentUser, setLoading);
  },[])

  return (
    loading?
   
      <div className="flex flex-row justify-center  mt-3 mb-3"> 
          <div className="spinner-grow inline-block w-8 h-8 bg-current rounded-full opacity-0" role="status">
              <span className="visually-hidden">Loading...</span>
          </div>
      </div>
   
    :
    <AppRouter currentUser={currentUser}/>
  );
}

export default App;
