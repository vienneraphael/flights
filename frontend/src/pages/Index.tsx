
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Plus, Users, Plane } from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface DateConstraint {
  min_date: string;
  max_date: string;
}

interface DurationConstraint {
  min_days: number;
  max_days: number;
}

interface PointOfInterest {
  arrival_name: string;
  departure_name: string;
  duration_constraint: DurationConstraint;
}

interface FlightSearchData {
  start_point: {
    name: string;
    date_constraint: DateConstraint;
  };
  points_of_interest: PointOfInterest[];
  end_point: {
    name: string;
    date_constraint: DateConstraint;
  };
}

const Index = () => {
  const navigate = useNavigate();
  const [passengers, setPassengers] = useState<number>(1);
  const [cabinClass, setCabinClass] = useState<string>('economy');
  const [startPoint, setStartPoint] = useState<string>('');
  const [startMinDate, setStartMinDate] = useState<string>('');
  const [startMaxDate, setStartMaxDate] = useState<string>('');
  const [endPoint, setEndPoint] = useState<string>('');
  const [endMinDate, setEndMinDate] = useState<string>('');
  const [endMaxDate, setEndMaxDate] = useState<string>('');
  const [legs, setLegs] = useState<PointOfInterest[]>([]);

  const validateIATA = (code: string): boolean => {
    return /^[A-Z]{3}$/.test(code);
  };

  const handleIATAInput = (value: string): string => {
    return value.toUpperCase().slice(0, 3);
  };

  const addLeg = () => {
    const newLeg: PointOfInterest = {
      arrival_name: '',
      departure_name: startPoint || '',
      duration_constraint: {
        min_days: 1,
        max_days: 7
      }
    };
    setLegs([...legs, newLeg]);
  };

  const updateLeg = (index: number, field: keyof PointOfInterest | 'min_days' | 'max_days', value: string | number) => {
    const updatedLegs = [...legs];
    if (field === 'min_days' || field === 'max_days') {
      updatedLegs[index].duration_constraint[field] = Number(value);
    } else {
      (updatedLegs[index] as any)[field] = field.includes('name') ? handleIATAInput(value as string) : value;
    }
    setLegs(updatedLegs);
  };

  const removeLeg = (index: number) => {
    setLegs(legs.filter((_, i) => i !== index));
  };

  const isFormValid = (): boolean => {
    if (!validateIATA(startPoint) || !validateIATA(endPoint)) return false;
    if (!startMinDate || !startMaxDate || !endMinDate || !endMaxDate) return false;

    for (const leg of legs) {
      if (!validateIATA(leg.arrival_name) || !validateIATA(leg.departure_name)) return false;
      if (leg.duration_constraint.min_days <= 0 || leg.duration_constraint.max_days <= 0) return false;
      if (leg.duration_constraint.min_days > leg.duration_constraint.max_days) return false;
    }

    return true;
  };

  const handleSearch = async () => {
    if (!isFormValid()) {
      toast({
        title: "Invalid form data",
        description: "Please fill in all required fields with valid data.",
        variant: "destructive"
      });
      return;
    }

    const searchData: FlightSearchData = {
      start_point: {
        name: startPoint,
        date_constraint: {
          min_date: startMinDate,
          max_date: startMaxDate
        }
      },
      points_of_interest: legs,
      end_point: {
        name: endPoint,
        date_constraint: {
          min_date: endMinDate,
          max_date: endMaxDate
        }
      }
    };

    console.log('Sending flight search request with data:', searchData);

    try {
      // Show loading state
      toast({
        title: "Searching for flights...",
        description: "Please wait while we find the best options for you."
      });

      const response = await fetch('https://flights-rxdt.onrender.com/flights/', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        body: JSON.stringify(searchData)
      });

      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error Response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const flightResults = await response.json();
      console.log('Flight results received:', flightResults);

      // Store both search data and API results in sessionStorage
      sessionStorage.setItem('flightSearchData', JSON.stringify(searchData));
      sessionStorage.setItem('flightResults', JSON.stringify(flightResults));

      navigate('/results');
    } catch (error) {
      console.error('Flight search failed:', error);
      toast({
        title: "Search failed",
        description: error instanceof Error ? error.message : "Unable to search for flights. Please try again.",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Plane className="h-8 w-8 text-blue-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-teal-600 bg-clip-text text-transparent">
              FlightSearch
            </h1>
          </div>
          <p className="text-lg text-gray-600">Plan your perfect multi-city journey</p>
        </div>

        <Card className="shadow-xl border-0 bg-white/80 backdrop-blur-sm">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-teal-600 text-white rounded-t-lg">
            <CardTitle className="text-2xl font-semibold">Flight Search</CardTitle>
          </CardHeader>
          <CardContent className="p-8 space-y-8">
            {/* Passenger and Cabin Selection */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="passengers" className="text-sm font-medium flex items-center gap-2">
                  <Users className="h-4 w-4" />
                  Passengers
                </Label>
                <Select value={passengers.toString()} onValueChange={(value) => setPassengers(Number(value))}>
                  <SelectTrigger className="h-12">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[...Array(10)].map((_, i) => (
                      <SelectItem key={i + 1} value={(i + 1).toString()}>
                        {i + 1} {i === 0 ? 'Passenger' : 'Passengers'}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="cabin-class" className="text-sm font-medium">
                  Cabin Class
                </Label>
                <Select value={cabinClass} onValueChange={setCabinClass}>
                  <SelectTrigger className="h-12">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="economy">Economy</SelectItem>
                    <SelectItem value="premium-economy">Premium Economy</SelectItem>
                    <SelectItem value="business">Business</SelectItem>
                    <SelectItem value="first">First Class</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Separator />

            {/* Start Point */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800">Departure</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start-point" className="text-sm font-medium">
                    From (IATA Code)
                  </Label>
                  <Input
                    id="start-point"
                    placeholder="CDG"
                    value={startPoint}
                    onChange={(e) => setStartPoint(handleIATAInput(e.target.value))}
                    className="h-12 text-center font-mono text-lg"
                    maxLength={3}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="start-min-date" className="text-sm font-medium">
                    Earliest Date
                  </Label>
                  <Input
                    id="start-min-date"
                    type="date"
                    value={startMinDate}
                    onChange={(e) => setStartMinDate(e.target.value)}
                    className="h-12"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="start-max-date" className="text-sm font-medium">
                    Latest Date
                  </Label>
                  <Input
                    id="start-max-date"
                    type="date"
                    value={startMaxDate}
                    onChange={(e) => setStartMaxDate(e.target.value)}
                    className="h-12"
                  />
                </div>
              </div>
            </div>

            {/* Dynamic Legs */}
            {legs.map((leg, index) => (
              <div key={index} className="space-y-4 p-6 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-gray-800">Stop {index + 1}</h3>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => removeLeg(index)}
                    className="text-red-600 border-red-200 hover:bg-red-50"
                  >
                    Remove
                  </Button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">From</Label>
                    <Input
                      placeholder="CDG"
                      value={leg.departure_name}
                      onChange={(e) => updateLeg(index, 'departure_name', e.target.value)}
                      className="h-12 text-center font-mono"
                      maxLength={3}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">To</Label>
                    <Input
                      placeholder="BCN"
                      value={leg.arrival_name}
                      onChange={(e) => updateLeg(index, 'arrival_name', e.target.value)}
                      className="h-12 text-center font-mono"
                      maxLength={3}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">Min Days</Label>
                    <Input
                      type="number"
                      min="1"
                      value={leg.duration_constraint.min_days}
                      onChange={(e) => updateLeg(index, 'min_days', e.target.value)}
                      className="h-12"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">Max Days</Label>
                    <Input
                      type="number"
                      min="1"
                      value={leg.duration_constraint.max_days}
                      onChange={(e) => updateLeg(index, 'max_days', e.target.value)}
                      className="h-12"
                    />
                  </div>
                </div>
              </div>
            ))}

            {/* Add Leg Button */}
            <div className="flex justify-center">
              <Button
                variant="outline"
                onClick={addLeg}
                className="h-12 px-8 border-2 border-dashed border-blue-300 text-blue-600 hover:bg-blue-50 hover:border-blue-400 transition-all duration-200"
              >
                <Plus className="h-5 w-5 mr-2" />
                Add Stop
              </Button>
            </div>

            <Separator />

            {/* End Point */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-800">Final Destination</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="end-point" className="text-sm font-medium">
                    To (IATA Code)
                  </Label>
                  <Input
                    id="end-point"
                    placeholder="LIS"
                    value={endPoint}
                    onChange={(e) => setEndPoint(handleIATAInput(e.target.value))}
                    className="h-12 text-center font-mono text-lg"
                    maxLength={3}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="end-min-date" className="text-sm font-medium">
                    Earliest Date
                  </Label>
                  <Input
                    id="end-min-date"
                    type="date"
                    value={endMinDate}
                    onChange={(e) => setEndMinDate(e.target.value)}
                    className="h-12"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="end-max-date" className="text-sm font-medium">
                    Latest Date
                  </Label>
                  <Input
                    id="end-max-date"
                    type="date"
                    value={endMaxDate}
                    onChange={(e) => setEndMaxDate(e.target.value)}
                    className="h-12"
                  />
                </div>
              </div>
            </div>

            {/* Search Button */}
            <div className="flex justify-center pt-6">
              <Button
                onClick={handleSearch}
                disabled={!isFormValid()}
                className="h-14 px-12 text-lg font-semibold bg-gradient-to-r from-blue-600 to-teal-600 hover:from-blue-700 hover:to-teal-700 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg transform transition-all duration-200 hover:scale-105"
              >
                <Plane className="h-5 w-5 mr-3" />
                Search for Optimal Path
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Index;
