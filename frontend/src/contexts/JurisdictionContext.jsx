import { createContext, useContext, useState, useCallback, useEffect } from 'react';

const JurisdictionContext = createContext();

export const JurisdictionProvider = ({ children }) => {
  const [selectedState, setSelectedState] = useState(localStorage.getItem('userState') || '');
  const [selectedDistrict, setSelectedDistrict] = useState(localStorage.getItem('userDistrict') || '');
  const [selectedType, setSelectedType] = useState('Assembly');
  const [year, setYear] = useState('2026');
  const [isLocating, setIsLocating] = useState(false);

  // Update local storage whenever state/district changes
  useEffect(() => {
    if (selectedState) localStorage.setItem('userState', selectedState);
    if (selectedDistrict) localStorage.setItem('userDistrict', selectedDistrict);
  }, [selectedState, selectedDistrict]);

  const autoDetectLocation = useCallback(async (silent = false) => {
    setIsLocating(true);
    if (!navigator.geolocation) {
      if (!silent) alert("Geolocation is not supported by your browser.");
      setIsLocating(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        try {
          const { latitude, longitude } = position.coords;
          const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10&addressdetails=1`);
          const data = await response.json();
          
          if (data && data.address) {
            const detectedState = data.address.state || data.address.county || '';
            const detectedCity = data.address.city || data.address.town || data.address.village || data.address.county || '';
            
            if (detectedState) setSelectedState(detectedState);
            if (detectedCity) setSelectedDistrict(detectedCity);
          }
        } catch (error) {
          console.error("Error fetching location details:", error);
          if (!silent) alert("Failed to auto-detect location details. Please enter manually.");
        } finally {
          setIsLocating(false);
        }
      },
      (error) => {
        console.error("Geolocation error:", error);
        if (!silent) alert("Location access denied or unavailable. Please enter your location manually.");
        setIsLocating(false);
      }
    );
  }, []);

  // Auto-detect on first visit if no location is set
  useEffect(() => {
    const hasVisited = localStorage.getItem('hasVisitedJurisdiction');
    if (!hasVisited && !selectedState && !selectedDistrict) {
      autoDetectLocation(true); // silent auto-detect, no annoying alerts if denied
      localStorage.setItem('hasVisitedJurisdiction', 'true');
    }
  }, [autoDetectLocation, selectedState, selectedDistrict]);

  return (
    <JurisdictionContext.Provider value={{ 
      selectedState, setSelectedState,
      selectedDistrict, setSelectedDistrict,
      selectedType, setSelectedType,
      year, setYear,
      autoDetectLocation, isLocating
    }}>
      {children}
    </JurisdictionContext.Provider>
  );
};

export const useJurisdiction = () => useContext(JurisdictionContext);
