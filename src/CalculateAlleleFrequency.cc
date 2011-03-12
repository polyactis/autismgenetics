/*
*
* 2011-3-11
*
*/


#include "CalculateAlleleFrequency.h"

CalculateAlleleFrequency::CalculateAlleleFrequency(float frequencyToSimulate, int noOfRows, int noOfCols, float minMAF)\
	:_frequencyToSimulate(frequencyToSimulate), _noOfRows(noOfRows), _noOfCols(noOfCols), _minMAF(minMAF)
{
	std::cerr<<"Program start ...\n";
	std::cerr<<"frequencyToSimulate=" <<_frequencyToSimulate << std::endl;

}

CalculateAlleleFrequency::~CalculateAlleleFrequency()
{
	_mafVector.clear();
	_dataMatrix.clear();
	std::cerr<<"exit.\n";
	//gsl_histogram_free (histogram);
}

vector<vi> CalculateAlleleFrequency::simulateDataMatrix(float frequencyToSimulate, int noOfRows, int noOfCols)
{
	std::cerr<<"Simulating "<< noOfRows << "X" << noOfCols << " matrix with maf=" <<frequencyToSimulate << "...";
	int intFrequency = frequencyToSimulate*100;
	int randomInt;
	int i,j;
	vector<vi> dataMatrix;
	//#pragma omp parallel for private(i) shared(dataMatrix)
	for(i=0;i<noOfRows;i++)
	{
		vi genotypeVector(noOfCols);
		//#pragma omp critical
		dataMatrix.push_back(genotypeVector);
	}
	int allele;

	boost::mt19937 rng;
	boost::uniform_real<> uni_dist(0,1);
	boost::variate_generator<boost::mt19937&, boost::uniform_real<> > uni(rng, uni_dist);

	#pragma omp parallel for private(j,i,allele,randomInt) \
		shared(dataMatrix,intFrequency, noOfCols, noOfRows) \
		schedule(dynamic,10)
	for (j=0;j<noOfCols;j++)
	{
		for(i=0;i<noOfRows;i++)
		{
			//randomInt = random()%100;	//rand()/random() causes the openmp version to be slower than serial one.
			if (uni()>=frequencyToSimulate)
			{
				allele = 1;
			}
			else
			{
				allele = 0;
			}
			dataMatrix[i][j] = allele;
		}
	}
	std::cerr<<"Done"<<std::endl;
	return dataMatrix;
}

vector<float> CalculateAlleleFrequency::calculateMAF(vector<vi> &dataMatrix)
{
	std::cerr<<"Calculating MAF for the matrix ... ";
	vector <float> mafVector(_noOfCols);
	int i,j;
	int noOfLociAboveMinMAF=0;
	std::map<int, float>::iterator a2fIter;
	int allele;
	#pragma omp parallel for private(j,i, allele, a2fIter) shared(mafVector) reduction(+: noOfLociAboveMinMAF)
	for (j=0;j<_noOfCols;j++)
	{
		std::map<int, float > allele2frequency;
		//tie(a2fIter, inserted) = allele2frequency.insert(std::make_pair(dataMatrix[i][j], ));
		//allele2frequency[0] = 0.0;
		//allele2frequency[1] = 1.0;
		for(i=0;i<_noOfRows;i++)
		{
			allele = dataMatrix[i][j];
			a2fIter = allele2frequency.find(allele);
			if (a2fIter==allele2frequency.end())
			{
				allele2frequency[allele] = 0;
			}
			else
			{
				allele2frequency[allele] += 1;
			}
		}
		float maf=1.0;	// max that maf could be.
		for(a2fIter=allele2frequency.begin();a2fIter!=allele2frequency.end();a2fIter++)
		{
			(*a2fIter).second /= float(_noOfRows);
			if ((*a2fIter).second<maf)
				maf =  a2fIter->second;
		}
		//allele2frequency[0] = allele2frequency[0]/float(_noOfRows);
		//allele2frequency[1] = allele2frequency[1]/float(_noOfRows);
		//float maf = std::min(allele2frequency[0], allele2frequency[1]);
		mafVector[j] = maf;
		//#pragma omp critical
		//{
		if (maf>=_minMAF)
		{
			noOfLociAboveMinMAF += 1;
		}
		//}
	}

	std::cerr<< noOfLociAboveMinMAF << " loci with MAF>= " << _minMAF<< ". Done"<<std::endl;

	return mafVector;
}

void CalculateAlleleFrequency::run()
{
	_dataMatrix = simulateDataMatrix(_frequencyToSimulate, _noOfRows, _noOfCols);
	_mafVector = calculateMAF(_dataMatrix);
}

void print_usage(FILE* stream,int exit_code)
{
	assert(stream !=NULL);
        fprintf(stream,"Usage: CalculateAlleleFrequency [OPTIONS] -f FREQUENCY\n");
	fprintf(stream,"\t-h  --help	Display the usage infomation.\n"\
		"\t-o ..., --output=...	Write output to file, maf.tsv(default)\n"\
		"\t-i ..., --input=...	input_filename\n"\
		"\t-f ..., --frequency=...	the minor allele frequency for simulation \n"\
		"\t-r ..., --no_of_rows=...	number of rows for simulation, 100(default)\n"\
		"\t-c ..., --no_of_cols=...	number of columns for simulation, 1000,000(default)\n"\
		"\t-m ..., --minMAF=...	minimum MAF 0.2(default)\n"\
		"\tFor long option, = or ' '(blank) is same.\n"\
		"\tLine tokenizer is one tab\n");
	exit(3);
}

int main(int argc, char* argv[])
{
	int next_option;
	const char* const short_options="ho:i:f:r:c:m:";
	const struct option long_options[]={
	  {"help",0,NULL,'h'},
	  {"output",1,NULL,'o'},
	  {"input",1,NULL,'i'},
	  {"frequency", 1, NULL, 'f'},
	  {"no_of_rows", 1, NULL, 'r'},
	  {"no_of_cols", 1, NULL, 'c'},
	  {"minMAF", 1, NULL, 'm'},
	  {NULL,0,NULL,0}
	};

	char* output_filename = "maf.tsv";
	char* input_filename = NULL;
	float frequency_to_simulate = 0.0;
	int no_of_rows=100;
	int no_of_cols=1000000;
	float minMAF = 0.2;
	do
	{
		next_option=getopt_long(argc,argv,short_options,long_options,NULL);
		switch(next_option)
		{
		case 'h':
			print_usage(stdout,0);
	  		exit(1);
		case 'o':
			output_filename=optarg;
			break;
		case 'i':
			input_filename = optarg;
			break;
		case 'f':
			frequency_to_simulate = atof(optarg);
			break;
		case 'r':
			no_of_rows = atoi(optarg);
			break;
		case 'c':
			no_of_cols = atoi(optarg);
			break;
		case 'm':
			minMAF = atof(optarg);
			break;
		case '?':
			print_usage(stderr,-1);
		case -1:
			break;
		default:
			abort();
		}
	}while(next_option!=-1);

	if (frequency_to_simulate>0.0)
	{

		CalculateAlleleFrequency instance(frequency_to_simulate, no_of_rows, no_of_cols, minMAF);
		instance.run();

	}
	else
		print_usage(stderr, 1);
}
