// CORE-SDK
import AgoraUIKit from 'agora-react-uikit';

const App = () => { 
  const rtcProps = {
    appId: 'e7f6e9aeecf14b2ba10e3f40be9f56e7', 
    channel: 'test', 
    token: '22167a22ee9f4aa19b26182b5dca259e', // enter your channel token as a string 
  }; 
  return (
    <AgoraUIKit rtcProps={rtcProps} /> 
  ) 
};

export default App; 