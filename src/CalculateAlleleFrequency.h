/*
 * 2011-3-11
 */
#include <stdio.h>
#include <stdlib.h>	//	2011-3-8 for rand()
#include <iostream>
#include <fstream>
#include <vector>
#include <bitset>
#include <string>
#include <map>		//for std::map
#include <queue>	//for priority_queue
#include <getopt.h>
#include <assert.h>
/*
#include <gsl/gsl_math.h>
#include <gsl/gsl_cdf.h>
#include <gsl/gsl_histogram.h>
#include <gsl/gsl_statistics_double.h>
*/
#include <algorithm>	//08-24-05 for std::copy
#include <iterator>	//08-24-05 for std::ostream_iterator
//#include <boost/tokenizer.hpp>	//08-24-05 for tokenizer, parse input file
//#include "boost/tuple/tuple.hpp"	//for boost::tuple	06-22-05
//#include <bvector.h>	//2007-01-17 needs this for bit_vector
#include <cmath>	//2007-01-17 abs() overloading needs this
#include <omp.h>

#include <boost/random/mersenne_twister.hpp>
#include <boost/random/linear_congruential.hpp>
#include <boost/random/uniform_int.hpp>
#include <boost/random/uniform_real.hpp>
#include <boost/random/variate_generator.hpp>

#include "boost/date_time/posix_time/posix_time.hpp"	//microsec_clock, time_duration, ptime


#include <boost/iostreams/concepts.hpp>   // multichar_input_filter
#include <boost/iostreams/operations.hpp> // read

using namespace std;
using namespace boost::posix_time;
namespace pt = boost::posix_time;
namespace io = boost::iostreams;

typedef vector<int> vi;
//typedef boost::tuple<std::string, std::string, float> edge_string_cor;

class CalculateAlleleFrequency
{
public:
	float _frequencyToSimulate;
	vector<vi> _dataMatrix;
	int _noOfRows;
	int _noOfCols;
	float _minMAF;
	vector<float> _mafVector;

	CalculateAlleleFrequency(float frequencyToSimulate, int noOfRows, int noOfCols, float minMAF);
	~CalculateAlleleFrequency();
	vector<vi> simulateDataMatrix(float frequencyToSimulate, int noOfRows, int noOfCols);
	vector<float> calculateMAF(vector<vi> &dataMatrix, float &minMAF);
	void run();

};
