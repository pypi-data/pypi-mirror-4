/** Copyright John Reid 2011, 128
 *
 * \file
 * \brief Tests branch and bound part of STEME algorithm.
 *
 */

#include <boost/assign/list_of.hpp>
#include <boost/test/utils/wrap_stringstream.hpp>
#include <boost/timer.hpp>

#include <steme/data.h>
#include <steme/model.h>
#include <steme/descender.h>
#include <steme/seqan_types.h>

#include <seqan/sequence.h>
#include <seqan/stream.h>
#include <seqan/seq_io/guess_stream_format.h> // had to add these 2 lines for it to compile with latest
#include <seqan/seq_io/read_fasta_fastq.h>    // svn trunk: rev12932

#include <fstream>

#define MAKE_STRING( x ) ( boost::wrap_stringstream().ref() << x ).str()

using namespace seqan;
using namespace std;
using namespace steme;

typedef steme_seqan_types<> seqan_types_t;

typedef seqan_types_t::id_set_t                     id_set_t;
typedef seqan_types_t::string_set_t                 string_set_t;
typedef seqan_types_t::string_t                     string_t;
typedef seqan_types_t::text_t                       text_t;                ///< The type of the text in the index.
typedef seqan_types_t::raw_text_t                   raw_text_t;            ///< The type of the raw text in the index.
typedef seqan_types_t::string_set_limits_t          string_set_limits_t;   ///< Used to convert between local and global positions.
typedef seqan_types_t::occurrences_t                occurrences_t;         ///< The type of a list of occurrences.
typedef seqan_types_t::local_pos_t                  local_pos_t;

typedef model<>::bg_model_t                         bg_model_t;            ///< The background model type.
typedef model<>::bs_model_t                         bs_model_t;            ///< The binding site model type.


/**
 * Read a FASTA file into a string set.
 */
void
read_fasta(
	const char * filename,
	id_set_t & ids,
	string_set_t & sequences
) {
	// Open file and create RecordReader.
	ifstream fasta( filename, std::ios_base::in | std::ios_base::binary );
	if(! fasta.good() )
		throw std::logic_error( "Could not open FASTA file." );
	RecordReader< ifstream, SinglePass<> > reader( fasta );
	// Define variables for storing the sequences and sequence ids.
	if( read2( ids, sequences, reader, Fasta() ) != 0 ) {
		throw std::logic_error( "ERROR reading FASTA." );
	}

}



void
print_seq_info( const char * filename, string_set_t & sequences ) {
	Size< string_t >::Type max_length = 0;
	Size< string_t >::Type total_bases = 0;
	for( Size< string_set_t >::Type i = 0; length( sequences ) != i; ++i ) {
		Size< string_t >::Type len = length( value( sequences, i ) );
		total_bases += len;
		max_length = std::max( max_length, len );
	}
	std::cout << "Read " << total_bases << " base pairs from " << length( sequences ) << " sequences from " << filename << "\n";
	std::cout << "Longest sequence has " << max_length << " base pairs\n";
}




struct visitor : tree_descender< visitor > {

	double log_Z_threshold;
	std::vector< double > positive_Z;
	std::vector< double > negative_Z;
	std::vector< double > positive_log_eval;
	std::vector< double > negative_log_eval;

	/** Constructor. */
	visitor(
		data<> &         _data,
		model<> &        _model,
		double                 Z_threshold
	)
	: tree_descender< visitor >( _data, _model )
	, log_Z_threshold( Z_threshold ? log( Z_threshold ) : - numeric_limits< double >::max() )
	, positive_Z( _data.N, 0. )
	, negative_Z( _data.N, 0. )
	, positive_log_eval( _data.N, 0. )
	, negative_log_eval( _data.N, 0. )
	{ }


	/**
	 * \return The threshold on log(expected[Z]).
	 */
	double
	get_log_Z_threshold() {
		return log_Z_threshold;
	}


    GCC_DIAG_OFF(uninitialized);
	template< bool RevComp >
	inline
	void
	handle_W_mer_occurrence_one_strand(
		int global_pos,
		double Z_strand,
		double g_n,
		double lambda,
		double log_lambda,
		double log_p_X_n_theta_BS,
		double log_p_background
	) {
		if( RevComp ) {
			negative_Z[ global_pos ] = Z_strand;
			negative_log_eval[ global_pos ] = log_p_X_n_theta_BS;
		} else {
			positive_Z[ global_pos ] = Z_strand;
			positive_log_eval[ global_pos ] = log_p_X_n_theta_BS;
		}
	}
    GCC_DIAG_ON(uninitialized);


	/// Handle a calculated Z for both strands of an occurrence of a W-mer
	inline
	void
	handle_W_mer_all_occurrences(
		top_down_it it,
		size_t num_occurrences,
		double Z_positive_total,
		double Z_negative_total
	) {
	}
};

namespace steme {
const double log_quarter = std::log( 0.25 ); /**< log(.25) */
}

void
check_Z( data<> & _data, size_t W, size_t pos, double Z_threshold, double Z, double calculated_Z, const char * strand ) {
	if( Z >= Z_threshold && calculated_Z != Z ) {
		std::string w_mer;
		assign( w_mer, _data.get_W_mer( W, pos ) );
		throw std::logic_error(
			MAKE_STRING(
				"Missing a Z on " << strand << " strand at global position " << pos
				<< "; W-mer=" << w_mer
				<< ": Z=" << Z
				<< "; calculated Z=" << calculated_Z
				<< "; threshold=" << Z_threshold
			)
		);
	}
}



int
main( int argc, char * argv[] ) {

	//const char * fasta_filename = "/home/john/Data/MEIS1/meis1-peaks.fasta";
	const char * fasta_filename = "/home/john/Dev/STEME/python/stempy/test/fasta/T00759-tiny.fa";
	if( argc > 1 ) {
		fasta_filename = argv[ 1 ];
	}


	//
	// Load sequences
	//
	string_set_t sequences;
	id_set_t ids;
	boost::timer timer;
	read_fasta( fasta_filename, ids, sequences );
	std::cout << "Took " << timer.elapsed() << " seconds to read FASTA file: " << fasta_filename << "\n";
	print_seq_info( fasta_filename, sequences );


	//
	// Build index
	//
	seqan_types_t::index_t index( sequences );


	//
	// Build stem object
	//
	data<> _data( index );


	//
	// Build background
	//
	const size_t W = 8;
	typedef complete_markov_model< 2, 4, double > markov_model_t;
	markov_model_t mm;
    zero_order_frequencies freqs = build_model_from_index( mm, index, 1. );
    zero_order_frequencies freqs_with_pseudo_counts = freqs.add_pseudo_counts( 1. );
	likelihoods_vec_vec_t lls;
	calculate_likelihoods( mm, _data.get_text(), lls );
	bg_model_t bg( W, freqs_with_pseudo_counts, &lls );
    base_to_wmer_likelihoods_calculator( _data, *bg.base_LLs, bg.wmer_LLs );

	//
	// Build model
	//
	bs_model_t bs( Pssm( PssmStorage( W, 4 ) ) );
	bs.seed( string_t( "AATTCCGG" ) );
	model<> _model( _data, bs, bg );


	//
	// Descend tree to find all Zs using a threshold of 0.
	//
	visitor all_Zs( _data, _model, 0. );
	all_Zs.descend_tree();


	//
	// Descend tree for a range of Zs and check all the Zs we were promised are there
	//
	using boost::assign::list_of;
	const std::vector< double > Z_thresholds = list_of( .00000001 )( .0001 )( .01 )( .05 )( .1 )( .2 )( .4 )( .6 )( .8 )( .9 )( .999999 )( 1. );
	BOOST_FOREACH( double Z_threshold, Z_thresholds ) {
		std::cout << "Testing Z threshold = " << Z_threshold << "\n";
		visitor v( _data, _model, Z_threshold );
		v.descend_tree();
		for( size_t pos = 0; all_Zs.positive_Z.size() != pos; ++pos ) {
			check_Z( _data, W, pos, Z_threshold, all_Zs.positive_Z[ pos ], v.positive_Z[ pos ], "positive" );
			check_Z( _data, W, pos, Z_threshold, all_Zs.negative_Z[ pos ], v.negative_Z[ pos ], "negative" );
		}
	}
}

