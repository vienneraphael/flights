
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, ArrowRight, Plane, Clock, DollarSign } from "lucide-react";

interface FlightOption {
  price: number;
  airline: string;
  flight_number: string;
}

interface Flight {
  departure_date: string;
  from_airport: string;
  to_airport: string;
  result: FlightOption[];
  url: string;
}

interface FlightScenario {
  flights: Flight[];
  min_total_price: number;
}

const Results = () => {
  const navigate = useNavigate();
  const [searchData, setSearchData] = useState<any>(null);
  const [scenarios, setScenarios] = useState<FlightScenario[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedSearchData = sessionStorage.getItem('flightSearchData');
    const storedResults = sessionStorage.getItem('flightResults');

    if (!storedSearchData || !storedResults) {
      navigate('/');
      return;
    }

    const searchData = JSON.parse(storedSearchData);
    const flightResults = JSON.parse(storedResults);

    console.log('Loaded search data:', searchData);
    console.log('Loaded flight results:', flightResults);

    setSearchData(searchData);
    setScenarios(flightResults);
    setLoading(false);
  }, [navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-xl font-semibold">Loading flight results...</div>
        </div>
      </div>
    );
  }

  if (!searchData || scenarios.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl font-semibold mb-4">No flight results found</div>
          <Button onClick={() => navigate('/')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Search
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Button
            variant="outline"
            onClick={() => navigate('/')}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Search
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Flight Results</h1>
            <p className="text-gray-600">
              Multi-city flight search results
            </p>
          </div>
        </div>

        {/* Search Summary */}
        <Card className="mb-8 bg-white/80 backdrop-blur-sm border-0 shadow-lg">
          <CardContent className="p-6">
            <div className="flex items-center justify-center gap-4 text-lg font-medium">
              <Badge variant="secondary" className="px-3 py-1">
                {searchData.start_point.name}
              </Badge>
              {searchData.points_of_interest.map((poi: any, index: number) => (
                <React.Fragment key={index}>
                  <ArrowRight className="h-4 w-4 text-gray-400" />
                  <Badge variant="secondary" className="px-3 py-1">
                    {poi.arrival_name}
                  </Badge>
                </React.Fragment>
              ))}
              <ArrowRight className="h-4 w-4 text-gray-400" />
              <Badge variant="secondary" className="px-3 py-1">
                {searchData.end_point.name}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Flight Scenarios */}
        <div className="space-y-8">
          {scenarios.map((scenario, scenarioIndex) => (
            <Card key={scenarioIndex} className="bg-white/90 backdrop-blur-sm border-0 shadow-xl">
              <CardHeader className="bg-gradient-to-r from-blue-600 to-teal-600 text-white">
                <div className="flex justify-between items-center">
                  <CardTitle className="text-xl">
                    Scenario {scenarioIndex + 1}
                  </CardTitle>
                  <div className="flex items-center gap-2 text-xl font-bold">
                    <DollarSign className="h-5 w-5" />
                    {scenario.min_total_price}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="p-6">
                {/* Flight Path */}
                <div className="flex items-center justify-center gap-4 mb-8 p-4 bg-gray-50 rounded-lg">
                  {scenario.flights.map((flight, flightIndex) => (
                    <React.Fragment key={flightIndex}>
                      <Badge variant="outline" className="px-3 py-1 font-mono text-sm">
                        {flight.from_airport}
                      </Badge>
                      <div className="flex items-center gap-2 text-gray-400">
                        <Plane className="h-4 w-4" />
                        <ArrowRight className="h-4 w-4" />
                      </div>
                      {flightIndex === scenario.flights.length - 1 && (
                        <Badge variant="outline" className="px-3 py-1 font-mono text-sm">
                          {flight.to_airport}
                        </Badge>
                      )}
                    </React.Fragment>
                  ))}
                </div>

                {/* Flight Options for Each Leg */}
                <div className="space-y-6">
                  {scenario.flights.map((flight, flightIndex) => (
                    <div key={flightIndex}>
                      <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <Plane className="h-5 w-5 text-blue-600" />
                        {flight.from_airport} → {flight.to_airport}
                        <Badge variant="outline" className="text-xs ml-2">
                          {flight.departure_date}
                        </Badge>
                      </h4>
                      <div className="grid gap-4">
                        {flight.result.map((option, optionIndex) => (
                          <div
                            key={optionIndex}
                            className={`p-4 rounded-lg border-2 transition-all duration-200 hover:shadow-md ${
                              optionIndex === 0
                                ? 'border-green-200 bg-green-50'
                                : 'border-gray-200 bg-white hover:border-blue-200'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-4">
                                <div className="font-mono font-bold text-lg">
                                  {option.flight_number}
                                </div>
                                <div className="text-gray-600">
                                  {option.airline}
                                </div>
                                {optionIndex === 0 && (
                                  <Badge className="bg-green-100 text-green-800 border-green-200">
                                    Cheapest
                                  </Badge>
                                )}
                              </div>
                              <div className="text-xl font-bold text-blue-600">
                                ${option.price}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      {flight.url && (
                        <div className="mt-4">
                          <Button
                            variant="outline"
                            onClick={() => window.open(flight.url, '_blank')}
                            className="w-full"
                          >
                            Book this flight
                          </Button>
                        </div>
                      )}
                      {flightIndex < scenario.flights.length - 1 && (
                        <Separator className="my-6" />
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Results;
