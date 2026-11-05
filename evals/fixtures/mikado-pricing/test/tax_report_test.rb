# frozen_string_literal: true

require "minitest/autorun"
require_relative "../lib/tax_report"

class TaxReportTest < Minitest::Test
  def test_heading_shows_the_rate
    assert_equal "VAT at 20%", TaxReport.new.heading
  end
end
